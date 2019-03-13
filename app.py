from flask import Flask, session
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_session import Session
from flask_loginmanager import LoginManager
from flask_admin.base import MenuLink
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import form
from wtforms import FileField
from flask_security import SQLAlchemyUserDatastore
from flask_security import Security
from flask_mail import Mail
import os

# Create class instance Flask with name app
# Load configurations from config file
app = Flask(__name__)
app.config.from_object(Configuration)

# Create database
db = SQLAlchemy(app)

# Create Migration db
migrate = Migrate(app, db, compare_type=True)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Init sessions
Session(app)

# Login manager
loginmanager = LoginManager()

# ADMIN
# Import all models
from models import *
# Import admin classes from admin
from admin import *

# Create admin panel
admin = Admin(app, 'Na Rogah', url='/', index_view=HomeAdminView(name='Home'))
admin.add_view(CategoryAdminView(Category, db.session))
admin.add_view(TimetableAdminView(Timetable, db.session))
admin.add_view(MenuAdminView(Menu, db.session))
admin.add_view(UsersAdminView(Users, db.session))
admin.add_view(TablesAdminView(Tables, db.session))
admin.add_view(BookingAdminView(Booking, db.session))
#logout link
admin.add_link(MenuLink(name='Logout', category='', url="/logout"))

# FLASK-SECURITY
user_datastore = SQLAlchemyUserDatastore(db, Users, Role)
security = Security(app, user_datastore)

# For sending emails with Flask-Mail
mail = Mail(app)

