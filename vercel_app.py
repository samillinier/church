from flask import jsonify, request, render_template, flash, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
import os
import sys
import traceback
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFError, CSRFProtect

# Initialize Flask app
app = Flask(__name__, static_folder='static')
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

# Add static file handling
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

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

def initialize_routes(app, db):
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
            log_info(f"Checking token: {token[:6]}...")  # Only log first 6 chars for security
            
            # Check if the token matches the secret key
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

            log_info("Starting database initialization from endpoint...")
            
            # Log database URL (without sensitive info)
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            masked_url = db_url.split('@')[1] if '@' in db_url else db_url
            log_info(f"Using database URL: ...@{masked_url}")
            
            # Drop all tables
            log_info("Dropping all existing tables...")
            db.drop_all()
            log_info("All tables dropped successfully")

            # Create all tables
            log_info("Creating database tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            log_info(f"Created tables: {tables}")
            
            if 'users' not in tables:
                log_error("Users table was not created!")
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to create users table'
                }), 500
            
            # Create admin user
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
            
            # Add and commit admin user
            db.session.add(admin)
            db.session.commit()
            log_info("Admin user created successfully!")
            
            # Verify admin user was created
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

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            try:
                # Log request details
            # Log environment variables (excluding sensitive data)
            env_vars = {k: '***' if any(s in k.lower() for s in ['password', 'secret', 'key', 'token', 'url']) else v 
                       for k, v in os.environ.items()}
            log_info(f"Environment variables: {env_vars}")

            # Check if database URL is set
            if not os.environ.get('DATABASE_URL'):
                log_error("DATABASE_URL environment variable is not set")
                return False

            # Test database connection with retries
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    log_info(f"Testing database connection (attempt {retry_count + 1}/{max_retries})...")
                    result = db.session.execute(text('SELECT 1'))
                    if result.scalar() == 1:
                        log_info("Database connection successful")
                        break
                    else:
                        log_error("Database connection test failed")
                        retry_count += 1
                except Exception as e:
                    log_error(f"Database connection error: {str(e)}")
                    log_error(traceback.format_exc())
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(1)  # Wait 1 second before retrying
                    else:
                        return False
            
            # Create tables if they don't exist
            log_info("Creating tables...")
            db.create_all()
            log_info("Tables created successfully")
            
            # Verify tables were created
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            log_info(f"Available tables: {tables}")
            
            # Check if users table exists and has the correct schema
            if 'users' not in tables:
                log_error("Users table was not created properly")
                return False
            
            # Create initial admin user if it doesn't exist
            log_info("Checking for admin user...")
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
            
            return True
            
        except Exception as e:
            log_error(f"Error during database initialization: {str(e)}")
            log_error("Traceback:")
            log_error(traceback.format_exc())
            try:
                db.session.rollback()
            except:
                pass
            return False

# Initialize the database
log_info("Starting database initialization...")
success = init_db()
if success:
    log_info("Database initialization completed successfully")
else:
    log_error("Database initialization failed")

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    # Add security headers from config
    for header, value in Config.SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

# Add request logging
@app.before_request
def log_request_info():
    log_info(f"Request: {request.method} {request.url}")
    log_info(f"Headers: {dict(request.headers)}")

# Add health check endpoint
@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        log_error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

# Add CSRF error handler
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    log_error(f"CSRF error: {str(e)}")
    return jsonify({
        'error': 'CSRF Error',
        'message': 'CSRF token validation failed. Please try again.',
        'status_code': 400
    }), 400

# Add database connection error handler
@app.errorhandler(OperationalError)
def handle_db_error(error):
    log_error(f"Database error: {str(error)}")
    log_error(traceback.format_exc())
    try:
        db.session.rollback()
    except:
        pass
    return jsonify({
        'error': 'Database Error',
        'message': 'A database error occurred. Please try again later.',
        'status_code': 500
    }), 500

# Add general exception handler
@app.errorhandler(Exception)
def handle_exception(error):
    log_error(f"Unhandled exception: {str(error)}")
    log_error(traceback.format_exc())
    try:
        db.session.rollback()
    except:
        pass
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred. Please try again later.',
        'status_code': 500
    }), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Log request details
            log_info("Login request received")
            log_info(f"Form data: {request.form}")
            
            # Get form data
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                log_error("Missing username or password")
                flash('Please provide both username and password', 'error')
                return render_template('login.html')
            
            log_info(f"Attempting login for user: {username}")
            
            # Log database configuration
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            masked_url = db_url.split('@')[1] if '@' in db_url else db_url
            log_info(f"Using database URL: ...@{masked_url}")
            
            # Test database connection
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
            
            # Check if users table exists
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            log_info(f"Available tables: {tables}")
            
            if 'users' not in tables:
                log_error("Users table does not exist")
                flash('Database setup required. Please contact administrator.', 'error')
                return render_template('login.html')
            
            # Try to find user
            try:
                user = User.query.filter_by(username=username).first()
                log_info(f"User query result: {user is not None}")
            except Exception as e:
                log_error(f"Error querying user: {str(e)}")
                log_error(traceback.format_exc())
                flash('An error occurred while looking up user. Please try again.', 'error')
                return render_template('login.html')
            
            if user:
                log_info(f"User found: {user.username}")
                if user.check_password(password):
                    login_user(user)
                    user.last_login = datetime.now(timezone.utc)
                    try:
                        db.session.commit()
                        log_info(f"Login successful for user: {username}")
                        next_page = request.args.get('next')
                        if next_page:
                            return redirect(next_page)
                        return redirect(url_for('dashboard'))
                    except Exception as e:
                        log_error(f"Database error during login: {str(e)}")
                        log_error(traceback.format_exc())
                        db.session.rollback()
                        flash('An error occurred during login. Please try again.', 'error')
                else:
                    log_error(f"Invalid password for user: {username}")
                    flash('Invalid username or password', 'error')
            else:
                log_error(f"User not found: {username}")
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add database initialization endpoint
@app.route('/initialize-database/<token>')
def initialize_database(token):
    try:
        log_info("Database initialization endpoint called")
        log_info(f"Checking token: {token[:6]}...")  # Only log first 6 chars for security
        
        # Check if the token matches the secret key
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

        log_info("Starting database initialization from endpoint...")
        
        # Log database URL (without sensitive info)
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        masked_url = db_url.split('@')[1] if '@' in db_url else db_url
        log_info(f"Using database URL: ...@{masked_url}")
        
        # Drop all tables
        log_info("Dropping all existing tables...")
        db.drop_all()
        log_info("All tables dropped successfully")

        # Create all tables
        log_info("Creating database tables...")
        db.create_all()
        
        # Verify tables were created
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        log_info(f"Created tables: {tables}")
        
        if 'users' not in tables:
            log_error("Users table was not created!")
            return jsonify({
                'status': 'error',
                'message': 'Failed to create users table'
            }), 500
        
        # Create admin user
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
        
        # Add and commit admin user
        db.session.add(admin)
        db.session.commit()
        log_info("Admin user created successfully!")
        
        # Verify admin user was created
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

@app.route('/healthz')
def healthz():
    return jsonify({
        'status': 'ok',
        'message': 'Application is running'
    })

# For local development
if __name__ == '__main__':
    app.run(debug=True) 