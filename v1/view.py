from app import app
from app import db
import json
from flask import request, jsonify, session, Response, send_from_directory
from models import Auth, Users
from models import Class, Menu
from app import *
from datetime import timedelta
from flask_security import login_required
import uuid


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


# Returns all dish categories
@app.route('/get_classes', methods=['GET'])
def get_classes():
    if request.method == 'GET':
        try:
            # Selest categories from DB
            food_class = Class.query.all()
        except Exception:
            return jsonify({'code': 500, 'desc': "Internal server error"}), 500
        class_item = {}
        sst = []
        # If categories wasn't detected
        if not food_class:
            return jsonify({'code': 204, 'desc': "No categories"}), 204
        for food_item in food_class:
            try:
                # Append dict by new values
                class_item["class_id"] = food_item.class_id
                class_item["name"] = food_item.name
                # Append list by class_item and delete class_item
                sst.append(class_item)
                class_item = {}
            except Exception:
                return jsonify({'code': 500, 'desc': "Internal server error"}), 500
        try:
            # Jsonificate result
            rezult = json.dumps(sst)
        except Exception:
            return jsonify({'code': 500, 'desc': "Cannot translate data in JSON"}), 500
        return Response(rezult, mimetype='application/json')


# Returns all menu items, associated with class_id
@app.route('/get_menu/<class_id>', methods=['GET'])
def get_menu(class_id):
    if request.method == 'GET':
        try:
            # Selest categories from DB
            menu = Menu.query.filter(Menu.class_id == class_id).all()
        except Exception:
            return jsonify({'code': 500, 'desc': "Internal server error"}), 500
        menu_item = {}
        menu_list = []
        for items in menu:
            try:
                # Append dict by new values
                menu_item["item_id"] = items.item_id
                menu_item["name"] = items.name
                menu_item["price"] = items.price
                menu_item["photo"] = items.photo
                menu_item["desc_short"] = items.desc_short
                menu_item["desc_long"] = items.desc_long
                menu_item["weight"] = items.weight
                menu_item["recommended"] = items.recommended
                # Append list by menu_item and delete menu_item
                menu_list.append(menu_item)
                menu_item = {}
            except Exception:
                return jsonify({'code': 500, 'desc': "Internal server error"}), 500
        try:
            # Jsonificate result
            rezult = json.dumps(menu_list)
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
    data = request.data
    jjs = json.loads(data)
    if jjs['kk'] == 'kk':
        return "OKAY"

    return 'f'


# Checks corect session data
def log_required(login, unique):
    if login in session:
        if session[login] == unique:
            return True
    return False


# Sends file from the directory to client
@app.route('/photos/<image>', methods=['GET', 'POST'])
def get_photo(image):
    return send_from_directory(app.config['UPLOAD_FOLDER'], image)
