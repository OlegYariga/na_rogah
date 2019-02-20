from flask import Flask, session
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_session import Session
from flask_loginmanager import LoginManager

# Create class instance Flask with name app
# Load configurations from config file
app = Flask(__name__)
app.config.from_object(Configuration)

# Create database
db = SQLAlchemy(app)

# Create Migration db
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Init sessions
Session(app)

# Login manager
loginmanager = LoginManager()
