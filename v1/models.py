from app import db
from datetime import datetime
from flask import jsonify
import json


# Class Auth stores user login and password
class Auth(db.Model):
    user_id = db.Column(db.BigInteger, primary_key=True)
    login = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    user = db.relationship('Users', backref='auth', uselist=False)

    def __init__(self, *args, **kwargs):
        super(Auth, self).__init__(*args, **kwargs)


# Class Users stores user data
class Users(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('auth.user_id'))
    reg_date = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    birthday = db.Column(db.DateTime)
    phone = db.Column(db.String(25))
    email = db.Column(db.String(64))


# Class Class stores info about dish categories
class Class(db.Model):
    class_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(64))
    menu = db.relationship('Menu', backref='Class', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Class, self).__init__(*args, **kwargs)


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


# Class stores photos
class Images(db.Model):
    image_id = db.Column(db.BigInteger, primary_key=True)
    fullname = db.Column(db.String(256))
    image_base64 = db.Column(db.LargeBinary)

    def __init__(self, fullname, image_binary):
        self.fullname = fullname
        self.image_base64 = image_binary
