class Configuration(object):
    # DEBUG = True
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://postgres:admin@localhost/narogah'
    # SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://yhrxhbrfbogimk:47626d88c9e87f23a71d76448009d0cabb6a2921bab9d2db261027c4d18f8536@ec2-46-137-158-249.eu-west-1.compute.amazonaws.com/df14qckbnogd15'
    SECRET_KEY = 'somethimngverysercrettext'
    SESSION_TYPE = 'filesystem'
    UPLOAD_FOLDER = 'C:\\Users\\Doc\\Desktop\\Zappa\\Na_Rogah\\app\\v1\\photos'
    # PATH = 'localhost:5000/photos/'
    PATH = 'https://na-rogah-api.herokuapp.com/photos/'
