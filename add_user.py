from app import app, db, User
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

def add_user(username, email, password, first_name, last_name, role='user', is_admin=False):
    with app.app_context():
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists")
            return False
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_admin=is_admin,
            created_at=datetime.now(timezone.utc),
            _is_active=True
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"User {username} created successfully")
            return True
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    # Example: Add a new user
    add_user(
        username='new_user',
        email='new_user@epaphra.com',
        password='user123',
        first_name='New',
        last_name='User',
        role='user',
        is_admin=False
    ) 