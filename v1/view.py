from app import app
from app import db
import json
from flask import request, jsonify, session, Response, make_response, send_from_directory
from werkzeug import secure_filename
from models import Auth, Users
from models import LastUpdate
from models import Class, Menu, Images
from app import *
from datetime import timedelta
from flask_security import login_required
import uuid
import os
import io
import base64


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)


# TEST METHOD
@app.route('/get_test', methods=['GET'])
def get_test():
    food_class = Class.query.all()
    for food in food_class:
        global result
        result += jsonify(food.name, food.class_id)
    return result


# Returns all dish categories (in array, for ANDROID
@app.route('/get_classes', methods=['GET'])
def get_classes():
    if request.method == 'GET':
        try:
            # Select categories from DB
            food_class = Class.query.order_by(Class.class_id).all()
        except Exception:
            return jsonify({'code': 500, 'desc': "Internal server error"}), 500
        food_set = []
        # If categories wasn't detected
        if not food_class:
            return jsonify({'code': 204, 'desc': "No categories"}), 204
        for food_item in food_class:
            try:
                # Append list by food_item (json)
                food_set.append(food_item.prepare_json())
            except Exception:
                return jsonify({'code': 500, 'desc': "Internal server error"}), 500
        try:
            # Jsonificate result
            rezult = json.dumps({'categories': food_set})
        except Exception:
            return jsonify({'code': 500, 'desc': "Cannot translate data in JSON"}), 500
        return Response(rezult, mimetype='application/json')


# Returns all menu items, associated with class_id
@app.route('/get_menu/<class_id>', methods=['GET'])
def get_menu(class_id):
    if request.method == 'GET':
        try:
            # Select menu from DB
            menu = Menu.query.filter(Menu.class_id == class_id).order_by(Menu.item_id).all()
        except Exception:
            return jsonify({'code': 500, 'desc': "Internal server error"}), 500
        menu_list = []
        for items in menu:
            try:
                # Append list by items and
                menu_list.append(items.prepare_json())
            except Exception:
                return jsonify({'code': 500, 'desc': "Internal server error"}), 500
        try:
            # Jsonificate result
            rezult = json.dumps({'menu': menu_list})
        except Exception:
            return jsonify({'code': 500, 'desc': "Cannot translate data in JSON"}), 500
        return Response(rezult, mimetype='application/json')


# User authorization with create session
@app.route('/auth', methods=['POST'])
def authorize():
    if request.method == 'POST':
        # Get data and convert them to JSON
        data = request.data
        json_data = json.loads(data)
        # Select record from DB, where login=login
        auth = Auth.query.filter(Auth.login == json_data['login']).first()
        if not auth:
            return jsonify({'code': 401, 'desc': "Login incorrect"}), 401
        # Check password incorrect
        if auth.password != json_data['password']:
            return jsonify({'code': 401, 'desc': "Password incorrect"}), 401
        # Generate unique identifier
        unique = str(uuid.uuid4())
        # Create new session with key <login> and unique value
        session[str(auth.login)] = unique
        # Create a response
        return jsonify({'code': 200, 'desc': "Authorized",
                        'login': str(auth.login), 'uuid': unique}), 200


@app.route('/hi', methods=['GET', 'POST'])
def hi():

    uuidstr = str(uuid.uuid4())[1:8]
    return uuidstr


# Checks correct session data
def log_required(login, unique):
    if login in session:
        if session[login] == unique:
            return True
    return False


# Sends file from the database to client
@app.route('/photos/<image>', methods=['GET', 'POST'])
def get_photo(image):
    if request.method == 'GET':
        try:
            # Get first base64 object photo with name <image> from database
            photo_base64 = Images.query.filter(Images.fullname == image).first()
        except Exception:
            return jsonify({'code': 500, 'desc': "Cannot read from DB"}), 500
        if photo_base64:  # if photo exists
            try:
                # Translate base64 object to photo
                photo = base64.b16decode(photo_base64.image_base64)
                # Make response and set headers
                response = make_response(photo)
                response.headers['Content-Transfer-Encoding'] = 'base64'
                response.headers['Content-Type'] = 'image'
            except Exception:
               return jsonify({'code': 500, 'desc': "Image was not recognized"}), 500
            # If okey, send photo to client
            return response
        return jsonify({'code': 203, 'desc': "Nothig discovered"}), 203
    return jsonify({'code': 405, 'desc': "Method not allowed"}), 405


# Admin pannel for uploading images
# REQUIRED SECURE INSTALL!!!
@app.route('/admin/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        try:
            # Get data from form
            file = request.files['file']
            menu_id = request.form['menu_id']
            # Select menu item with id = menu_id
            menu = Menu.query.filter(Menu.item_id == int(menu_id)).first()
        except Exception:
           return jsonify({'code': 401, 'desc': "Incorrect data"}), 401
        # if file was selected
        if file:
            # if menu item exists
            if menu:
                try:
                    # Generate unique sequence with 7 signs (garbage)
                    uuidstr = str(uuid.uuid4())[1:8]
                    # Check filename and add garbage
                    filename = uuidstr + secure_filename(file.filename)
                    # Translate photo in base64 object
                    base = base64.b16encode(file.read())
                    # Call constructor Images with filename and base64 object
                    image = Images(menu.item_id, str(filename), base)
                    # Add data to DB
                    db.session.add(image)
                    db.session.commit()
                    # Update field menu_photo in Menu table with new PATH to photo
                    menu.photo = str(app.config['PATH']+str(filename))
                    db.session.add(menu)
                    db.session.commit()
                    # Change last update date
                    update = LastUpdate().update_db()
                except Exception:
                   return jsonify({'code': 405, 'desc': "Cannot process this file"}), 405
            else:
                return jsonify({'code': 203, 'desc': "No such item detected"}), 203
    # Bring form for uploading a new file
    # ADD MESSAGE IF OKAY
    return Response('''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=number name=menu_id>
         <input type=file name=file>
         <input type=submit value=Upload>
    </form>
    ''')


# Sends to a cliet last db update (date and time)
@app.route('/check_update', methods=['GET'])
def check_update():
    update = LastUpdate().check_update()
    return update
