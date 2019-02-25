from flask import Flask, session
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_session import Session
from flask_loginmanager import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import form
from wtforms import FileField


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

# Import all models
from models import *
# Import admin classes from admin
from admin import *

# Create admin panel
admin = Admin(app)
admin.add_view(ClassAdminView(Class, db.session))
admin.add_view(MenuAdminView(Menu, db.session))
admin.add_view(ImageAdminView(Images, db.session))
