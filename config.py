import os
from datetime import timedelta
import secrets
import urllib.parse

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or secrets.token_hex(32)
    WTF_CSRF_ENABLED = True
    
    # Get the database URL from environment variable or use SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///church.db')
    
    # Convert postgres:// to postgresql:// for SQLAlchemy
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Parse the URL to handle SSL configuration
    parsed = urllib.parse.urlparse(DATABASE_URL)
    if parsed.scheme in ('postgresql', 'postgres'):
        # Start with the base URL
        url_parts = list(parsed)
        
        # Parse the query parameters
        query_dict = dict(urllib.parse.parse_qsl(parsed.query))
        
        # Add SSL requirements
        query_dict.update({
            'sslmode': 'require'
        })
        
        # Rebuild the query string
        url_parts[4] = urllib.parse.urlencode(query_dict)
        
        # Reconstruct the URL
        DATABASE_URL = urllib.parse.urlunparse(url_parts)
    
    # Set the SQLAlchemy database URI
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Enable SQL query logging
    
    # Configure SQLAlchemy connection pool
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Enable automatic reconnection
        'pool_recycle': 300,    # Recycle connections every 5 minutes
        'pool_timeout': 30,     # Connection timeout of 30 seconds
        'pool_size': 10,        # Pool size
        'max_overflow': 5,      # Allow 5 connections above pool size
        'connect_args': {
            'connect_timeout': 10,  # Connection timeout in seconds
            'sslmode': 'require'    # Require SSL
        }
    }
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/tmp/uploads' if os.environ.get('RENDER') else 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    }

    # Debug configuration
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    TESTING = False
    
    # Logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True
            },
            'sqlalchemy.engine': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }

    # File upload settings - use /tmp for Vercel
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = PERMANENT_SESSION_LIFETIME
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True 