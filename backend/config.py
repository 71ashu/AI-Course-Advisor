"""Application configuration."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def _get_database_url():
    url = os.getenv('DATABASE_URL', '')
    # Some cloud providers (e.g. Heroku, Railway) still issue postgres:// URLs,
    # which SQLAlchemy 1.4+ requires to be postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url or 'postgresql://localhost/course_advisor'

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

    # Password reset emails (optional; when unset, reset links are only returned in debug responses)
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    PASSWORD_RESET_TOKEN_HOURS = int(os.getenv('PASSWORD_RESET_TOKEN_HOURS', '1'))
    MAIL_SERVER = os.getenv('MAIL_SERVER', '')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('1', 'true', 'yes')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')
