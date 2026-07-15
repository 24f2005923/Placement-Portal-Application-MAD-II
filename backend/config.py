import os
from datetime import timedelta

# Configuration settings for the Placement Portal Application
# All important settings like db path, secret keys, upload folder are here

class Config:

    # secret key used by flask for security - change before going live
    SECRET_KEY = os.environ.get('SECRET_KEY', 'placement@portal2024')

    # database setup - using sqlite which is easy for development
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_FILE = os.path.join(BASE_DIR, 'database', 'placement.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_FILE
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # jwt token settings
    # access token is valid for 8 hours, refresh token for 30 days
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt@portal2024')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # resume upload folder and file size limit (5 MB)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'resumes')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

    # allow requests from the vue frontend running on port 5173
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']
