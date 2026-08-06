import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(_env_path, override=True)


class Config:
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_FILE  = os.path.join(ROOT_DIR, 'database', 'placement.db')

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'placement-portal-secret-key-2024!'

    SQLALCHEMY_DATABASE_URI      = f'sqlite:///{DB_FILE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY          = os.environ.get('JWT_SECRET_KEY') or 'jwt-placement-portal-secret-key-2024!'
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    SEED_ADMIN = os.environ.get('SEED_ADMIN', 'true').lower() == 'true'
    DEFAULT_ADMIN_EMAIL = os.environ.get('DEFAULT_ADMIN_EMAIL') or 'admin@admin.com'
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD') or 'password'
    DEFAULT_ADMIN_NAME = os.environ.get('DEFAULT_ADMIN_NAME') or 'Portal Admin'

    UPLOAD_FOLDER       = os.path.join(ROOT_DIR, 'uploads', 'resumes')
    MAX_CONTENT_LENGTH  = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS  = {'pdf', 'doc', 'docx'}

    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]

    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    CELERY_BROKER_URL    = os.environ.get('CELERY_BROKER_URL')    or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/1'

    CELERY_RESULT_EXPIRES = int(os.environ.get('CELERY_RESULT_EXPIRES') or 3600)

    CACHE_TTL_SHORT   = 120
    CACHE_TTL_MEDIUM  = 300
    CACHE_TTL_LONG    = 600

    MAIL_SERVER   = os.environ.get('MAIL_SERVER')   or 'smtp.gmail.com'
    MAIL_PORT     = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_SENDER   = os.environ.get('MAIL_SENDER')   or 'noreply@placement-portal.local'

    GCHAT_WEBHOOK_URL = os.environ.get('GCHAT_WEBHOOK_URL') or ''

    SMS_PROVIDER       = os.environ.get('SMS_PROVIDER')       or 'console'
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or ''
    TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN')  or ''
    TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER') or ''

    EXPORTS_FOLDER = os.path.join(ROOT_DIR, 'exports')
    REPORTS_FOLDER = os.path.join(ROOT_DIR, 'reports')
