import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Get the database URL from environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Handle both postgres:// and postgresql:// style URLs
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        # Add SSL configuration if not present
        if '?' not in DATABASE_URL:
            DATABASE_URL += '?sslmode=require'
        elif 'sslmode=' not in DATABASE_URL:
            DATABASE_URL += '&sslmode=require'
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Use SQLite for local development with absolute path
        basedir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "church.db")}'
    
    # File upload settings - use /tmp for Vercel
    UPLOAD_FOLDER = '/tmp' if os.environ.get('VERCEL_ENV') == 'production' else 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Additional settings
    SESSION_COOKIE_SECURE = os.environ.get('VERCEL_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True 