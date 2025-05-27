from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timezone
import os
import sys
import traceback
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def log_info(message):
    print(f"[INFO] {message}", file=sys.stdout)
    sys.stdout.flush()

def log_error(message):
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.stderr.flush()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))
    role = db.Column(db.String(20), default='user')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    _is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        return self._is_active

@app.route('/')
def index():
    log_info("Accessing root route")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            log_info("Login request received")
            log_info(f"Form data: {request.form}")
            
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                log_error("Missing username or password")
                flash('Please provide both username and password', 'error')
                return render_template('login.html')
            
            log_info(f"Attempting login for user: {username}")
            
            try:
                log_info("Testing database connection...")
                result = db.session.execute(text('SELECT 1'))
                if result.scalar() == 1:
                    log_info("Database connection successful")
                else:
                    log_error("Database connection test failed")
                    flash('Database connection error. Please try again later.', 'error')
                    return render_template('login.html')
            except Exception as e:
                log_error(f"Database connection error during login: {str(e)}")
                log_error(traceback.format_exc())
                flash('Database connection error. Please try again later.', 'error')
                return render_template('login.html')
            
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            log_info(f"Available tables: {tables}")
            
            if 'users' not in tables:
                log_error("Users table does not exist")
                flash('Database setup required. Please contact administrator.', 'error')
                return render_template('login.html')
            
            try:
                user = User.query.filter_by(username=username).first()
                log_info(f"User query result: {user is not None}")
            except Exception as e:
                log_error(f"Error querying user: {str(e)}")
                log_error(traceback.format_exc())
                flash('An error occurred while looking up user. Please try again.', 'error')
                return render_template('login.html')
            
            if user and user.check_password(password):
                login_user(user)
                user.last_login = datetime.now(timezone.utc)
                try:
                    db.session.commit()
                    log_info(f"Login successful for user: {username}")
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('dashboard'))
                except Exception as e:
                    log_error(f"Database error during login: {str(e)}")
                    log_error(traceback.format_exc())
                    db.session.rollback()
                    flash('An error occurred during login. Please try again.', 'error')
            else:
                log_error(f"Invalid credentials for user: {username}")
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            log_error(f"Unexpected error during login: {str(e)}")
            log_error(traceback.format_exc())
            flash('An unexpected error occurred. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/healthz')
def healthz():
    return jsonify({
        'status': 'ok',
        'message': 'Application is running'
    })

@app.route('/initialize-database/<token>')
def initialize_database(token):
    try:
        log_info("Database initialization endpoint called")
        log_info(f"Checking token: {token[:6]}...")
        
        init_token = os.environ.get('INIT_DB_TOKEN')
        if not init_token:
            log_error("INIT_DB_TOKEN environment variable is not set")
            return jsonify({
                'status': 'error',
                'message': 'INIT_DB_TOKEN not configured'
            }), 500
            
        if token != init_token:
            log_error("Invalid token for database initialization")
            return jsonify({
                'status': 'error',
                'message': 'Invalid token'
            }), 403

        log_info("Starting database initialization...")
        
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        masked_url = db_url.split('@')[1] if '@' in db_url else db_url
        log_info(f"Using database URL: ...@{masked_url}")
        
        log_info("Dropping all existing tables...")
        db.drop_all()
        
        log_info("Creating database tables...")
        db.create_all()
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        log_info(f"Created tables: {tables}")
        
        if 'users' not in tables:
            log_error("Users table was not created!")
            return jsonify({
                'status': 'error',
                'message': 'Failed to create users table'
            }), 500
        
        log_info("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@epaphra.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_admin=True,
            created_at=datetime.now(timezone.utc),
            _is_active=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        log_info("Admin user created successfully!")
        
        admin_check = User.query.filter_by(username='admin').first()
        if not admin_check:
            log_error("Admin user verification failed!")
            return jsonify({
                'status': 'error',
                'message': 'Failed to verify admin user creation'
            }), 500
            
        log_info("Database initialization completed successfully!")
        return jsonify({
            'status': 'success',
            'message': 'Database initialized successfully',
            'tables': tables
        })
        
    except Exception as e:
        log_error(f"Database initialization failed: {str(e)}")
        log_error(traceback.format_exc())
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True) 