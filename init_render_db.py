from app import app, db, User
from datetime import datetime, timezone
import os
import sys
import traceback
from sqlalchemy import text, inspect

def log_info(message):
    print(f"[INFO] {message}", file=sys.stdout)
    sys.stdout.flush()

def log_error(message):
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.stderr.flush()

def init_render_db():
    with app.app_context():
        try:
            # Log database URL (without sensitive info)
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            masked_url = db_url.split('@')[1] if '@' in db_url else db_url
            log_info(f"Using database URL: ...@{masked_url}")

            # Test database connection
            log_info("Testing database connection...")
            result = db.session.execute(text('SELECT 1'))
            if result.scalar() == 1:
                log_info("Database connection successful!")
            else:
                log_error("Database connection test failed!")
                return False

            # Drop all tables if they exist
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
                return False
            
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
            if admin_check:
                log_info("Admin user verification successful!")
                return True
            else:
                log_error("Admin user verification failed!")
                return False
                
        except Exception as e:
            log_error(f"Database initialization failed: {str(e)}")
            log_error(f"Traceback: {traceback.format_exc()}")
            try:
                db.session.rollback()
            except:
                pass
            return False

if __name__ == "__main__":
    success = init_render_db()
    if success:
        log_info("Database initialization completed successfully!")
    else:
        log_error("Database initialization failed!") 