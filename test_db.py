from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

def test_database_connection():
    app = Flask(__name__)
    
    # Get database URL from environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL environment variable is not set")
        return False
    
    # Handle both postgres:// and postgresql:// style URLs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Add SSL configuration if not present
    if '?' not in DATABASE_URL:
        DATABASE_URL += '?sslmode=require'
    elif 'sslmode=' not in DATABASE_URL:
        DATABASE_URL += '&sslmode=require'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    try:
        # Try to execute a simple query
        with app.app_context():
            result = db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful!")
            print(f"Result: {result.scalar()}")
            return True
    except Exception as e:
        print("❌ Database connection failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_database_connection() 