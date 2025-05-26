from flask import Flask, jsonify
from app import app, db, User, Notification
from datetime import datetime, timezone
import os
from config import Config
import traceback
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        try:
            # Check if database URL is set
            if not os.environ.get('SUPABASE_DB_URL'):
                print("ERROR: SUPABASE_DB_URL environment variable is not set")
                return False

            # Check connection first
            print("Testing database connection...")
            try:
                result = db.session.execute(text('SELECT 1'))
                if result.scalar() != 1:
                    raise Exception("Database connection test failed")
                print("Database connection successful")
            except Exception as e:
                print(f"Database connection error: {str(e)}")
                print(traceback.format_exc())
                return False
            
            # Create tables if they don't exist
            print("Creating tables...")
            db.create_all()
            print("Tables created successfully")
            
            # Verify tables were created
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Available tables: {tables}")
            
            # Check if users table exists and has the correct schema
            if 'users' not in tables:
                print("ERROR: Users table was not created properly")
                return False
            
            # Create initial admin user if it doesn't exist
            print("Checking for admin user...")
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("Creating admin user...")
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
                print("Admin user created successfully")
            else:
                print("Admin user already exists")
            
            return True
            
        except Exception as e:
            print(f"Error during database initialization: {str(e)}")
            print("Traceback:")
            print(traceback.format_exc())
            try:
                db.session.rollback()
            except:
                pass
            return False

# Configure the Flask app first
app.config.from_object(Config)

# Initialize the database
print("Starting database initialization...")
success = init_db()
if success:
    print("Database initialization completed successfully")
else:
    print("Database initialization failed")

# Add error handlers
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error)
    }), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'Not Found',
        'message': str(error)
    }), 404

# For Vercel serverless deployment
app = app

# For local development
if __name__ == '__main__':
    app.run(debug=True) 