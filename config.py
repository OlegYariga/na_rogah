import os


class Configuration(object):
    # Flask-configuration settings
    DEBUG = True
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_TYPE = 'filesystem'
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SECURITY_PASSWORD_HASH = 'plaintext'
    
    #PATH = 'localhost:5000/api/v1/photos/'
    PATH = 'https://na-rogah-api.herokuapp.com/api/v1/photos/'

    # Flask VENV Settings
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    # Email VENV Settings
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

