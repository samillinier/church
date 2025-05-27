from app import app, db, User
from sqlalchemy import text, inspect
import sys
import traceback

def log_info(message):
    print(f"[INFO] {message}", file=sys.stdout)
    sys.stdout.flush()

def log_error(message):
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.stderr.flush()

def test_render_db():
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

            # Check existing tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            log_info(f"Existing tables: {tables}")

            # Check if users table exists
            if 'users' not in tables:
                log_error("Users table does not exist!")
                return False
            
            # Check if admin user exists
            log_info("Checking for admin user...")
            admin = User.query.filter_by(username='admin').first()
            if admin:
                log_info("Admin user exists!")
                log_info(f"Admin details: username={admin.username}, email={admin.email}, role={admin.role}")
                return True
            else:
                log_error("Admin user does not exist!")
                return False

        except Exception as e:
            log_error(f"Database test failed: {str(e)}")
            log_error(f"Traceback: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    success = test_render_db()
    if success:
        log_info("All database tests passed!")
    else:
        log_error("Database tests failed!") 