from app import app, db, User, Notification
from datetime import datetime, timezone
import os
from config import Config
import traceback
from werkzeug.security import generate_password_hash

# Use configuration from config.py
app.config.from_object(Config)

def init_db():
    with app.app_context():
        try:
            print("Creating tables...")
            db.create_all()
            print("Tables created successfully")
            
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("Creating admin user...")
                # Create initial admin user
                admin = User(
                    username='admin',
                    email='admin@epaphra.com',
                    first_name='Admin',
                    last_name='User',
                    role='admin',
                    is_admin=True,
                    created_at=datetime.now(timezone.utc)
                )
                # Set password using the set_password method
                admin.set_password('admin123')
                db.session.add(admin)
                
                try:
                    db.session.commit()
                    print("Admin user created successfully with:")
                    print("Username: admin")
                    print("Password: admin123")
                    
                    # Create welcome notification
                    welcome = Notification(
                        type='system',
                        title='Welcome to EPAPHRA',
                        message='Welcome to the church management system.',
                        date=datetime.now(timezone.utc),
                        user_id=admin.id,
                        is_read=False,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.session.add(welcome)
                    db.session.commit()
                    print("Welcome notification created")
                except Exception as e:
                    print(f"Error during commit: {str(e)}")
                    print(traceback.format_exc())
                    db.session.rollback()
                    raise
            else:
                print("Admin user already exists")
                
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            print(traceback.format_exc())
            db.session.rollback()

# Initialize database
try:
    print("Starting database initialization...")
    init_db()
    print("Database initialization completed")
except Exception as e:
    print(f"Database initialization error: {str(e)}")

# This is important for Vercel
app = app 