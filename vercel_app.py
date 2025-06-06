from app import app, db, User, Notification
from datetime import datetime
import os

# Configure PostgreSQL for production
if os.environ.get('VERCEL_ENV') == 'production':
    db_url = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_XEz5n2xivYJW@ep-cool-river-a89e69pj-pooler.eastus2.azure.neon.tech/neondb?sslmode=require')
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
                    role='admin',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                
                # Create finance admin
                finance_admin = User(
                    username='finance_admin',
                    email='finance.admin@epaphra.com',
                    first_name='Finance',
                    last_name='Admin',
                    role='finance_admin'
                )
                finance_admin.set_password('finance123')
                db.session.add(finance_admin)
                
                # Create finance officer
                finance_officer = User(
                    username='finance_officer',
                    email='finance.officer@epaphra.com',
                    first_name='Finance',
                    last_name='Officer',
                    role='finance_officer'
                )
                finance_officer.set_password('finance123')
                db.session.add(finance_officer)
                
                db.session.commit()
                print("Initial users created successfully!")

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
            raise e

# Initialize the database
init_db()

# This is important for Vercel
app = app 