import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    PLATFORM_NAME = os.getenv('PLATFORM_NAME', 'Learning Lounge by ismail')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///lounge.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 256 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('PRODUCTION') == '1'
    RATELIMIT_STORAGE_URI = os.getenv('REDIS_URL', 'memory://')
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    JUDGE0_URL = os.getenv('JUDGE0_URL', '')
    JUDGE0_TOKEN = os.getenv('JUDGE0_TOKEN', '')
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'ollama')
    AI_MODEL = os.getenv('AI_MODEL', '')
    AI_ENDPOINT = os.getenv('AI_ENDPOINT', 'http://localhost:11434')
    AI_TIMEOUT = int(os.getenv('AI_TIMEOUT', '45'))
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    PUBLIC_URL = os.getenv('PUBLIC_URL', 'http://localhost:5066')
    MAIL_HOST = os.getenv('MAIL_HOST', '')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '1025'))
    MAIL_FROM = os.getenv('MAIL_FROM', 'learning@localhost')
