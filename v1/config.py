class Configuration(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgres+psycopg2://hiwtapmbtiopzw:24f8a0de2eae7cdb8964d1d595be39dedd6b4145a0c8519408cf5cbc7f7ae08d@ec2-79-125-6-250.eu-west-1.compute.amazonaws.com/d3l1ljosug4cte'
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = 'somethimngverysercret'
	UPLOAD_FOLDER = 'https://na-rogah-api.herokuapp.com/photos'
    # UPLOAD_FOLDER = 'C:\\Users\\Doc\\Desktop\\Zappa\\Na_Rogah\\app\\v1\\photos'
