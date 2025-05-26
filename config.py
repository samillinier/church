import os
from datetime import timedelta
import secrets
import urllib.parse

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or secrets.token_hex(32)
    WTF_CSRF_ENABLED = True
    
    # Get the database URL from environment variable
    DATABASE_URL = os.environ.get('SUPABASE_DB_URL')
    if not DATABASE_URL:
        raise ValueError("No SUPABASE_DB_URL set for Flask application")
    
    # Parse the database URL to ensure it's properly formatted
    parsed_url = urllib.parse.urlparse(DATABASE_URL)
    
    # Handle both postgres:// and postgresql:// style URLs
    if parsed_url.scheme == 'postgres':
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Add SSL configuration if not present
    query_params = urllib.parse.parse_qs(parsed_url.query)
    if 'sslmode' not in query_params:
        if '?' not in DATABASE_URL:
            DATABASE_URL += '?sslmode=require'
        else:
            DATABASE_URL += '&sslmode=require'
    
    # Set the SQLAlchemy database URI
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('FLASK_ENV') == 'development'  # Only log SQL in development
    
    # Configure SQLAlchemy connection pool with SSL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Enable automatic reconnection
        'pool_recycle': 300,    # Recycle connections every 5 minutes
        'pool_timeout': 30,     # Connection timeout of 30 seconds
        'pool_size': 10,        # Reduced pool size for serverless
        'max_overflow': 5,      # Allow 5 connections above pool size
        'connect_args': {
            'connect_timeout': 10,
            'sslmode': 'require',
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'application_name': 'epospea'  # Identify the application in database logs
        }
    }
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/tmp/uploads' if os.environ.get('VERCEL') else 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    }

    # File upload settings - use /tmp for Vercel
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = PERMANENT_SESSION_LIFETIME
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True 