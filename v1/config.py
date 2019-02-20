class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://postgres:admin@localhost/narogah'
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = 'somethimngverysercret'
