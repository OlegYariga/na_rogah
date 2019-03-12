import uuid
import json
import base64
from datetime import datetime

from flask import request, jsonify
from werkzeug import secure_filename
from flask_security import UserMixin, RoleMixin

from app import db
from app import *


items_orders = db.Table('items_orders',
                       db.Column('item_id', db.BigInteger(), db.ForeignKey('items.id')),
                       db.Column('order_id', db.BigInteger(), db.ForeignKey('orders.id'))
                       )


class Items(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(28))
    count = db.Column(db.Integer)
    order = db.relationship('Orders', secondary=items_orders, backref=db.backref('items', lazy='dynamic'))


# This table stores relations Users and Roles
orders_users = db.Table('orders_users',
                       db.Column('order_id', db.BigInteger(), db.ForeignKey('orders.id')),
                       db.Column('user_id', db.BigInteger(), db.ForeignKey('users.id'))
                       )


class Orders(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    order_date = db.Column(db.DateTime)
    table_num = db.Column(db.Integer)
    total = db.Column(db.Integer)
    user = db.relationship('Users', secondary=orders_users, backref=db.backref('orders', lazy='dynamic'))


# This table stores relations Users and Roles
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.BigInteger(), db.ForeignKey('users.id')),
                       db.Column('role_id', db.BigInteger(), db.ForeignKey('role.id'))
                       )


# Class USER stores user credentials and info
class Users(db.Model, UserMixin):
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    reg_date = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    birthday = db.Column(db.DateTime)
    phone = db.Column(db.String(25))
    # For Flask-Security
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    active = db.Column(db.Boolean(), default=False)
    booking = db.relationship('Booking', backref='users', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)

    def __repr__(self):
        return str('email: '+str(self.email)+', '+str(self.name)+' тел: '+str(self.phone))


# Stores user roles
class Role(db.Model, RoleMixin):
    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return self.name


# Class Category stores info about dish categories
class Category(db.Model):
    category_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    order = db.Column(db.Integer)
    menu = db.relationship('Menu', backref='Category', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)

    def prepare_menu_items_json(self):
        try:
            menu = Menu.query.filter(self.category_id == Menu.category_id).order_by(Menu.name).all()
            items_list = []
            for item in menu:
                items_list.append(item.prepare_json())

            result = json.dumps({'category_id': self.category_id, 'category_name': self.name,
                                 'category_dishes': items_list})
            return result
        except Exception:
            return ""

    def prepare_json(self):
        return {
            'class_id': self.category_id,
            'name': self.name,
            'order': self.order
        }

    def __repr__(self):
        return self.name


# Class Menu stores info about menu items
class Menu(db.Model):
    item_id = db.Column(db.BigInteger, primary_key=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey(Category.category_id))
    name = db.Column(db.String(28), nullable=False)
    price = db.Column(db.Integer)
    photo = db.Column(db.Text)
    desc_short = db.Column(db.String(50))
    desc_long = db.Column(db.String(180))
    weight = db.Column(db.String(36))
    recommended = db.Column(db.String(64))
    image = db.relationship('Images', backref='menu', uselist=False)
    delivery = db.Column(db.Boolean, default=True)

    def prepare_json(self):
        _class = Category.query.filter(Category.category_id == self.category_id).first()
        return {
            'item_id': self.item_id,
            'class_name': _class.name,
            'name': self.name,
            'price': self.price,
            'photo': self.photo,
            'desc_short': self.desc_short,
            'desc_long': self.desc_long,
            'weight': self.weight,
            'recommended': self.recommended,
            'delivery': self.delivery
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


class Tables(db.Model):
    table_id = db.Column(db.BigInteger, primary_key=True)
    chair_type = db.Column(db.String(32))
    chair_count = db.Column(db.Integer)
    position = db.Column(db.String(64))
    booking = db.relationship('Booking', backref='tables', lazy='dynamic')

    def __repr__(self):
        return str('Столик № '+str(self.table_id)+',  '+str(self.chair_count)+' мест,  '+str(self.position))

    def prepare_json(self):
        return {
            'table_id': self.table_id,
            'chair_type': self.chair_type,
            'chair_count': self.chair_count,
            'position': self.position
        }


class Booking(db.Model):
    booking_id = db.Column(db.BigInteger, primary_key=True)
    date = db.Column(db.Date)
    time_from = db.Column(db.Time)
    time_to = db.Column(db.Time)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    table_id = db.Column(db.BigInteger, db.ForeignKey('tables.table_id'))
    accepted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return str(str(self.date)+'  '+str(self.time_from)+' - '+str(self.time_to))
