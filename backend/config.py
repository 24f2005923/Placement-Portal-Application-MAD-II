import os
from datetime import timedelta

# Application configuration file
class Config:
    # Setup working directory paths
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_FILE = os.path.join(ROOT_DIR, 'database', 'placement.db')
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'placement@portal2024'
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_FILE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Security Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt@portal2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Upload handling
    UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'uploads', 'resumes')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    # Cross-Origin Resource Sharing
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]

