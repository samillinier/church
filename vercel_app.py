from flask import Flask
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
            # Check connection first
            print("Testing database connection...")
            result = db.session.execute(text('SELECT 1'))
            if result.scalar() != 1:
                raise Exception("Database connection test failed")
            print("Database connection successful")
            
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
                raise Exception("Users table was not created properly")
            
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
            db.session.rollback()
            return False

# Initialize the database
print("Starting database initialization...")
success = init_db()
if success:
    print("Database initialization completed successfully")
else:
    print("Database initialization failed")
    # Don't raise an exception here, let the application continue

# Configure the Flask app
app.config.from_object(Config)

# For Vercel serverless deployment
app = app

# For local development
if __name__ == '__main__':
    app.run(debug=True) 