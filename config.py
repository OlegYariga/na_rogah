import os


class Configuration(object):
    # Flask-configuration settings
    DEBUG = True
    # DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'somethimngverysercrettext'
    SESSION_TYPE = 'sqlalchemy'
    SECURITY_PASSWORD_SALT = 'sequritipasswordsalttonotbeenencrypted852753951'
    SECURITY_PASSWORD_HASH = 'plaintext'
    #PATH = 'localhost:5000/api/v1/photos/'
    PATH = 'https://na-rogah-api.herokuapp.com/api/v1/photos/'

    # Flask VENV Settings
    # SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    # SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://postgres:admin@localhost/narogah'
    # SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://yhrxhbrfbogimk:47626d88c9e87f23a71d76448009d0cabb6a2921bab9d2db261027c4d18f8536@ec2-46-137-158-249.eu-west-1.compute.amazonaws.com/df14qckbnogd15'

    # Email VENV Settings
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    """
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    # MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'oyariga@gmail.com'
    MAIL_PASSWORD = 'qwertyui1234'
    MAIL_DEFAULT_SENDER = 'oyariga@gmail.com'
    """
