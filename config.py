import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key-change-this'
    
    # OpenRouter AI Configuration
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
    GOOGLE_SCOPE = os.environ.get('GOOGLE_SCOPE')
    GOOGLE_AUTH_URI = os.environ.get('GOOGLE_AUTH_URI')
    GOOGLE_TOKEN_URI = os.environ.get('GOOGLE_TOKEN_URI')
    
    # File upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Email types configuration
    EMAIL_TYPES = [
        'professional', 'comedy', 'friendly', 'formal', 'casual', 
        'marketing', 'apology', 'thank_you', 'invitation', 'follow_up'
    ]
    
    # Application settings
    APP_NAME = os.environ.get('APP_NAME', 'AI Email Generator')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
