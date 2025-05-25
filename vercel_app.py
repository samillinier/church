from app import app, db, User, Notification
from datetime import datetime

def init_db():
    with app.app_context():
        try:
            # Create new tables
            db.create_all()
            
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # Create initial users
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

        except Exception as e:
            print("Error initializing database:", str(e))
            db.session.rollback()

# Initialize database
init_db()

# This is important for Vercel
app = app 