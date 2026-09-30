import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///security_monitor.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ML Models path
    MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results'))
