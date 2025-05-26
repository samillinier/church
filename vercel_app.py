from flask import Flask, jsonify, request
from app import app, db, User, Notification
from datetime import datetime, timezone
import os
import sys
from config import Config
import traceback
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from werkzeug.security import generate_password_hash

def log_info(message):
    print(f"[INFO] {message}", file=sys.stdout)
    sys.stdout.flush()

def log_error(message):
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.stderr.flush()

def init_db():
    with app.app_context():
        try:
            # Log environment variables (excluding sensitive data)
            env_vars = {k: '***' if 'PASSWORD' in k or 'URL' in k else v 
                       for k, v in os.environ.items()}
            log_info(f"Environment variables: {env_vars}")

            # Check if database URL is set
            if not os.environ.get('SUPABASE_DB_URL'):
                log_error("SUPABASE_DB_URL environment variable is not set")
                return False

            # Check connection first
            log_info("Testing database connection...")
            try:
                result = db.session.execute(text('SELECT 1'))
                if result.scalar() != 1:
                    raise Exception("Database connection test failed")
                log_info("Database connection successful")
            except Exception as e:
                log_error(f"Database connection error: {str(e)}")
                log_error(traceback.format_exc())
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

# Configure the Flask app first
app.config.from_object(Config)

# Initialize the database
log_info("Starting database initialization...")
success = init_db()
if success:
    log_info("Database initialization completed successfully")
else:
    log_error("Database initialization failed")

@app.before_request
def log_request_info():
    log_info(f"Request: {request.method} {request.url}")
    log_info(f"Headers: {dict(request.headers)}")

# Add error handlers
@app.errorhandler(500)
def internal_error(error):
    log_error(f"500 error: {str(error)}")
    log_error(traceback.format_exc())
    db.session.rollback()
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error)
    }), 500

@app.errorhandler(404)
def not_found_error(error):
    log_error(f"404 error: {str(error)}")
    return jsonify({
        'error': 'Not Found',
        'message': str(error)
    }), 404

# For Vercel serverless deployment
app = app

# For local development
if __name__ == '__main__':
    app.run(debug=True) 