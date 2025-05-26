from app import app, db, User, Notification
from datetime import datetime
import os

# Configure PostgreSQL for production
if os.environ.get('VERCEL_ENV') == 'production':
    db_url = os.environ.get('DATABASE_URL')
    # ElephantSQL uses postgres:// but SQLAlchemy requires postgresql://
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'

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
                    password='admin123'  # This will be hashed by the model
                )
                db.session.add(admin)
                db.session.commit()

        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise e

# Initialize the database
init_db()

# This is important for Vercel
app = app 