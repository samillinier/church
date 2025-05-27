from app import app, db, User
from datetime import datetime, timezone
import os

def init_database():
    with app.app_context():
        print(f"Using database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
        
        # Check if admin user exists
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
                created_at=datetime.now(timezone.utc)
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            try:
                db.session.commit()
                print("Admin user created successfully!")
            except Exception as e:
                print(f"Error creating admin user: {str(e)}")
                db.session.rollback()
                raise
        else:
            print("Admin user already exists")

if __name__ == "__main__":
    init_database()