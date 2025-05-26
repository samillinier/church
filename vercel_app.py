from app import app, db, User, Notification
from datetime import datetime
import os

# Configure PostgreSQL for production
if os.environ.get('VERCEL_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
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
                    role='admin',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                
                # Create welcome notification
                welcome = Notification(
                    type='system',
                    title='Welcome to EPAPHRA',
                    message='Welcome to the church management system. Start by exploring the dashboard.',
                    date=datetime.utcnow(),
                    user_id=1,  # This will be the admin's ID
                    is_read=False
                )
                
                db.session.add(welcome)
                db.session.commit()
                print("Initial admin user and notification created successfully!")

        except Exception as e:
            print("Error initializing database:", str(e))
            db.session.rollback()

# Initialize database
init_db()

# This is important for Vercel
app = app 