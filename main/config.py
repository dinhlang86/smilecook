import os

class Config:
    
    DEBUG = False
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_ERROR_MESSAGE_KEY = 'message'
    
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    UPLOADED_IMAGES_DEST = 'static/images'
    
    # User SimpleCache strategy
    CACHE_TYPE = 'SimpleCache'
    # 10 min
    CACHE_DEFAULT_TIMEOUT = 10 * 60
    
    RATELIMIT_HEADERS_ENABLED = True
 
    
class DevelopmentConfig(Config):
    
    DEBUG = True
    
    SECRET_KEY = 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://TienPham:dinhlang@localhost/smilecook'


class ProductConfig(Config):
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
# Imitate the production environment for testing  
class StagingConfig(Config):
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    