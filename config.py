import os
from datetime import timedelta
import secrets

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or secrets.token_hex(32)
    WTF_CSRF_ENABLED = True
    
    # Get the database URL from environment variable
    DATABASE_URL = os.environ.get('SUPABASE_DB_URL')
    if not DATABASE_URL:
        raise ValueError("No SUPABASE_DB_URL set for Flask application")
    
    # Handle both postgres:// and postgresql:// style URLs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Add SSL configuration if not present
    if '?' not in DATABASE_URL:
        DATABASE_URL += '?sslmode=require'
    elif 'sslmode=' not in DATABASE_URL:
        DATABASE_URL += '&sslmode=require'
    
    # Set the SQLAlchemy database URI
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Log all SQL queries
    
    # Configure SQLAlchemy connection pool with SSL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 5,
        'connect_args': {
            'connect_timeout': 10,
            'sslmode': 'require',
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    }
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Upload config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/tmp/uploads' if os.environ.get('VERCEL') else 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

    # File upload settings - use /tmp for Vercel
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = PERMANENT_SESSION_LIFETIME
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True 