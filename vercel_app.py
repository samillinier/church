from app import app, db, User, Notification
from datetime import datetime
import os
from config import Config

# Use configuration from config.py
app.config.from_object(Config)

def init_db():
    with app.app_context():
        try:
            # Create new tables
            db.create_all()
            
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # Create initial admin user
                admin = User(
                    username='admin',
                    email='admin@epaphra.com',
                    first_name='Admin',
                    last_name='User',
                    role='admin',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully!")

                # Create welcome notification
                welcome = Notification(
                    type='system',
                    title='Welcome to EPAPHRA',
                    message='Welcome to the church management system.',
                    date=datetime.utcnow(),
                    user_id=admin.id,
                    is_read=False
                )
                db.session.add(welcome)
                db.session.commit()
                print("Welcome notification created!")

        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise e

# Initialize the database
init_db()

# This is important for Vercel
app = app 