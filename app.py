from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timezone
import os
import sys
import traceback
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError, ProgrammingError
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import logging.config
import json

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.config.dictConfig(app.config['LOGGING_CONFIG'])
logger = logging.getLogger(__name__)

# Initialize extensions
try:
    db = SQLAlchemy(app)
    csrf = CSRFProtect(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    logger.info("Successfully initialized Flask extensions")
except Exception as e:
    logger.error(f"Failed to initialize Flask extensions: {str(e)}")
    logger.error(traceback.format_exc())
    raise

def log_info(message):
    logger.info(message)

def log_error(message, exc_info=False):
    logger.error(message, exc_info=exc_info)

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response status: {response.status}")
    return response

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}", exc_info=True)
    if app.debug:
        # In debug mode, show the actual error
        return f"""
        <h1>Internal Server Error</h1>
        <h2>Error: {str(error)}</h2>
        <pre>{traceback.format_exc()}</pre>
        """, 500
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Page not found: {request.url}")
    return render_template('404.html'), 404

@app.errorhandler(SQLAlchemyError)
def handle_db_error(error):
    logger.error(f"Database error: {str(error)}", exc_info=True)
    db.session.rollback()
    if app.debug:
        # In debug mode, show the actual error
        return f"""
        <h1>Database Error</h1>
        <h2>Error: {str(error)}</h2>
        <pre>{traceback.format_exc()}</pre>
        """, 500
    return render_template('500.html'), 500

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
    try:
        # Test database connection
        log_info("Testing database connection...")
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        log_info("Database connection successful")

        # Check tables
        log_info("Checking database tables...")
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        log_info(f"Found tables: {tables}")

        # Check users table specifically
        if 'users' not in tables:
            log_error("Users table not found")
            return jsonify({
                'status': 'unhealthy',
                'database': 'connected',
                'error': 'Users table not found',
                'tables': tables
            }), 500

        # Test users table query
        log_info("Testing users table query...")
        result = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        log_info(f"Found {result} users")

        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'tables': tables,
            'user_count': result
        })
    except Exception as e:
        log_error(f"Health check failed: {str(e)}")
        log_error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/init-db')
def init_db():
    try:
        log_info("Starting database initialization...")
        
        # Create tables
        log_info("Creating database tables...")
        db.create_all()
        
        # Verify tables were created
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        log_info(f"Created tables: {tables}")
        
        if 'users' not in tables:
            log_error("Failed to create users table")
            return jsonify({
                'status': 'error',
                'message': 'Failed to create users table'
            }), 500
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
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
            log_info("Admin user created successfully")
        else:
            log_info("Admin user already exists")
        
        return jsonify({
            'status': 'success',
            'message': 'Database initialized successfully',
            'tables': tables
        })
        
    except Exception as e:
        log_error(f"Database initialization failed: {str(e)}")
        log_error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/debug-info')
def debug_info():
    """Endpoint to show debug information"""
    if not app.debug:
        return "Debug mode is disabled", 403
        
    info = {
        'Database URL': app.config['SQLALCHEMY_DATABASE_URI'],
        'Debug Mode': app.debug,
        'Testing Mode': app.testing,
        'Secret Key Set': bool(app.config['SECRET_KEY']),
        'Environment': os.environ.get('FLASK_ENV', 'not set'),
        'Database Options': app.config['SQLALCHEMY_ENGINE_OPTIONS'],
    }
    
    return f"""
    <h1>Debug Information</h1>
    <pre>{json.dumps(info, indent=2)}</pre>
    """

if __name__ == '__main__':
    app.run(debug=True) 