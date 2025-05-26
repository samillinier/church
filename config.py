import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_XEz5n2xivYJW@ep-cool-river-a89e69pj-pooler.eastus2.azure.neon.tech/neondb?sslmode=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 