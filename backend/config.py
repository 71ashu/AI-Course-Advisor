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
