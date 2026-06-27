import os
from dotenv import load_dotenv

# Identify base directory to locate .env
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sehat-saathi-super-secret-key-987654321')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Ensure correct database path relative to instance folder or base folder
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
        db_file = SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        if not os.path.isabs(db_file):
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(base_dir, db_file)}"
            
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
