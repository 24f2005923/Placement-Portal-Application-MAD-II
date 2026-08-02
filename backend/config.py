import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend/ directory (where this file lives).
# This must happen before any os.environ.get() calls so that all
# environment variables defined in .env are visible to the rest of
# the configuration — including the Celery worker process.
_env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(_env_path, override=False)   # override=False: real env vars win over .env


# ─────────────────────────────────────────────────────────────────
# Application Configuration
# All sensitive values are read from environment variables.
# Defaults are provided only for local development convenience.
# ─────────────────────────────────────────────────────────────────
class Config:
    # ── Directory Paths ─────────────────────────────────────────
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_FILE  = os.path.join(ROOT_DIR, 'database', 'placement.db')

    # ── Flask Core ───────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'placement-portal-secret-key-2024!'

    # ── SQLAlchemy ───────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI      = f'sqlite:///{DB_FILE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT ──────────────────────────────────────────────────────
    JWT_SECRET_KEY          = os.environ.get('JWT_SECRET_KEY') or 'jwt-placement-portal-secret-key-2024!'
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # ── File Uploads ─────────────────────────────────────────────
    UPLOAD_FOLDER       = os.path.join(ROOT_DIR, 'uploads', 'resumes')
    MAX_CONTENT_LENGTH  = 5 * 1024 * 1024          # 5 MB
    ALLOWED_EXTENSIONS  = {'pdf', 'doc', 'docx'}

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]

    # ── Redis ────────────────────────────────────────────────────
    # Used for both the Celery broker/backend and the response cache.
    # Set REDIS_URL in your .env file when deploying.
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # ── Celery ───────────────────────────────────────────────────
    # Database 0  → broker (job queue)
    # Database 1  → result backend (task results)
    CELERY_BROKER_URL    = os.environ.get('CELERY_BROKER_URL')    or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/1'

    # How long Celery keeps task results in Redis (seconds)
    CELERY_RESULT_EXPIRES = int(os.environ.get('CELERY_RESULT_EXPIRES') or 3600)  # 1 hour

    # ── Redis Cache TTL constants (seconds) ──────────────────────
    CACHE_TTL_SHORT   = 120    #  2 min  — live data that changes frequently
    CACHE_TTL_MEDIUM  = 300    #  5 min  — dashboard summaries
    CACHE_TTL_LONG    = 600    # 10 min  — report statistics

    # ── Email (SMTP) ─────────────────────────────────────────────
    # Configure these in your .env file to enable real email sending.
    # If MAIL_USERNAME is empty the system logs emails to the console.
    MAIL_SERVER   = os.environ.get('MAIL_SERVER')   or 'smtp.gmail.com'
    MAIL_PORT     = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''   # leave blank for console mode
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_SENDER   = os.environ.get('MAIL_SENDER')   or 'noreply@placement-portal.local'

    # ── Google Chat Webhook ──────────────────────────────────────
    # Set to your Google Chat space webhook URL to enable notifications.
    # Leave blank to skip Google Chat messages.
    GCHAT_WEBHOOK_URL = os.environ.get('GCHAT_WEBHOOK_URL') or ''

    # ── SMS Provider ─────────────────────────────────────────────
    # SMS_PROVIDER options: 'console' (default) | 'twilio'
    # 'console' simply prints SMS messages to the log — no account needed.
    SMS_PROVIDER       = os.environ.get('SMS_PROVIDER')       or 'console'
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or ''
    TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN')  or ''
    TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER') or ''

    # ── Export & Report directories ──────────────────────────────
    EXPORTS_FOLDER = os.path.join(ROOT_DIR, 'exports')
    REPORTS_FOLDER = os.path.join(ROOT_DIR, 'reports')
