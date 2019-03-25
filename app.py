import atexit
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
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import JWTManager

# Create class instance Flask with name app
# Load configurations from config file
app = Flask(__name__)
app.config.from_object(Configuration)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'


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
admin.add_view(TimetableAdminView(Timetable, db.session, name='Расписание работы'))
admin.add_view(TablesAdminView(Tables, db.session, name='Столы'))
admin.add_view(CategoryAdminView(Category, db.session, name='Категории'))
admin.add_view(MenuAdminView(Menu, db.session, name='Меню'))
admin.add_view(UsersAdminView(Users, db.session, name='Пользователи'))
admin.add_view(BookingAdminView(Booking, db.session, name='Бронирование'))
#logout link
admin.add_link(MenuLink(name='Выйти', category='', url="/logout"))

# FLASK-SECURITY
user_datastore = SQLAlchemyUserDatastore(db, Users, Role)
security = Security(app, user_datastore)

# For sending emails with Flask-Mail
mail = Mail(app)

# import function for delete old booking records from db
from background_invoker import delete_old_booking
# BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_old_booking, trigger="interval", seconds=30)
scheduler.start()


# JWT
jwt = JWTManager(app)

#initialized store for user access codes
#user_access_code = UserRegAccessCode()
