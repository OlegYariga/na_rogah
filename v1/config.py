class Configuration(object):
    # DEBUG = True
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://postgres:admin@localhost/narogah'
    SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://lselsjnaieikfj:d63b9e42bbd21b61816dbf3177141e3773604275ee673617a3d9cf8fbf8a6859@ec2-46-137-170-51.eu-west-1.compute.amazonaws.com/d95c9jl6vpo64i'
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = 'somethimngverysercret'
    UPLOAD_FOLDER = 'C:\\Users\\Doc\\Desktop\\Zappa\\Na_Rogah\\app\\v1\\photos'
    # PATH = 'localhost:5000/photos/'
    PATH = 'https://na-rogah-api.herokuapp.com/photos/'
