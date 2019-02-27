from app import db
from app import *
from datetime import datetime
from flask import jsonify, make_response
import json
import base64
from flask import request, jsonify, session, Response, make_response, send_from_directory
import uuid
from werkzeug import secure_filename
from flask_security import UserMixin, RoleMixin

# This table stores relations Users and Roles
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.BigInteger(), db.ForeignKey('users.id')),
                       db.Column('role_id', db.BigInteger(), db.ForeignKey('role.id'))
                       )


# Class USER stores user credentials and info
class Users(db.Model, UserMixin):
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(256))
    reg_date = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    birthday = db.Column(db.DateTime)
    phone = db.Column(db.String(25))

    # For Flask-Security
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    active = db.Column(db.Boolean())

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)


class Role(db.Model, RoleMixin):
    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))


# Class Class stores info about dish categories
class Class(db.Model):
    class_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(64))
    menu = db.relationship('Menu', backref='Class', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Class, self).__init__(*args, **kwargs)

    def prepare_json(self):
        return {
            'class_id': self.class_id,
            'name': self.name
        }

    def __repr__(self):
        return self.name


# Class Menu stores info about menu items
class Menu(db.Model):
    item_id = db.Column(db.BigInteger, primary_key=True)
    class_id = db.Column(db.BigInteger, db.ForeignKey(Class.class_id))
    name = db.Column(db.String(128))
    price = db.Column(db.Float)
    photo = db.Column(db.Text)
    desc_short = db.Column(db.Text)
    desc_long = db.Column(db.Text)
    weight = db.Column(db.Integer)
    recommended = db.Column(db.String(64))
    image = db.relationship('Images', backref='menu', uselist=False)

    def prepare_json(self):
        _class = Class.query.filter(Class.class_id == self.class_id).first()
        return {
            'item_id': self.item_id,
            'class_name': _class.name,
            'name': self.name,
            'price': self.price,
            'photo': self.photo,
            'desc_short': self.desc_short,
            'desc_long': self.desc_long,
            'weight': self.weight,
            'recommended': self.recommended
        }

    def load_image(self):
        try:
            file = request.files['file']
            if file:
                # Generate unique sequence with 7 signs (garbage)
                uuidstr = str(uuid.uuid4())[1:8]
                # Check filename and add garbage
                filename = uuidstr + secure_filename(file.filename)
                # Translate photo in base64 object
                base = base64.b16encode(file.read())
                # Call constructor Images with filename and base64 object
                image = Images(self.item_id, str(filename), base)
                # Add data to DB
                db.session.add(image)
                db.session.commit()
                # Update field menu_photo in Menu table with new PATH to pho
                # Change last update date
                update = LastUpdate().update_db()
                # Update field menu_photo in Menu table with new PATH to photo
                self.photo = str(app.config['PATH']+str(filename))
        except Exception:
            return 'NOT OK'
        return 'OK'

    def delete_image(self):
        try:
            # Select images from DB where image.item_id == Menu.item_id
            images = Images.query.filter(self.item_id == Images.item_id).delete()
        except Exception:
            return 'NOT OK'

    def __repr__(self):
        return self.name


# Class stores photos
class Images(db.Model):
    image_id = db.Column(db.BigInteger, primary_key=True)
    item_id = db.Column(db.BigInteger, db.ForeignKey('menu.item_id'))
    fullname = db.Column(db.String(256))
    image_base64 = db.Column(db.LargeBinary)

    def __init__(self, item_id, fullname, image_binary):
        self.item_id = item_id
        self.fullname = fullname
        self.image_base64 = image_binary


# Class for store DateTime
class LastUpdate(db.Model):
    log_id = db.Column(db.BigInteger, primary_key=True)
    log_date_time = db.Column(db.DateTime)

    def update_db(self):
        last_date = self.query.first()
        if last_date:
            last_date.log_date_time = datetime.now()
            db.session.add(last_date)
            db.session.commit()
        else:
            self.log_date_time = datetime.now()
            db.session.add(self)
            db.session.commit()

    def check_update(self):
        last_date = self.query.first()
        if last_date:
            return str(last_date.log_date_time)
        else:
            return str("")
