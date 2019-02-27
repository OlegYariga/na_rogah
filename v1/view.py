import json
from flask import request, jsonify, session, Response, make_response, send_from_directory
from werkzeug import secure_filename
from models import Users
from models import LastUpdate
from models import Class, Menu, Images
from app import *
from datetime import timedelta
from flask_security import login_required
import uuid
import base64


# Make session permanent with lifetime=1 before request
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)


# Returns all dish categories (in array)
@app.route('/get_classes', methods=['GET'])
def get_classes():
    try:
        # Select categories from DB
        food_class = Class.query.order_by(Class.class_id).all()
        # Create empty list
        food_set = []
        for food_item in food_class:
            # Append list by food_item (json)
            food_set.append(food_item.prepare_json())
        # Jsonificate result
        result = json.dumps({'categories': food_set})
    except TypeError:
        # If program cannot translate data to json or can't append list
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        # If there're other SERVER errors
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500
    # If OKAY, send data to client
    return Response(result, mimetype='application/json')


# Returns all menu items, associated with class_id
@app.route('/get_menu/<class_id>', methods=['GET'])
def get_menu(class_id):
    try:
        # Select menu from DB where class_id == <class_id>
        menu = Menu.query.filter(Menu.class_id == int(class_id)).order_by(Menu.item_id).all()
        # Create empty list
        menu_list = []
        for items in menu:
            # Append list by new items (json)
            menu_list.append(items.prepare_json())
        # Jsonificate result
        result = json.dumps({'menu': menu_list})
    except ValueError:
        # If GET parameter was wrong
        return jsonify({'code': 415, 'desc': "Not int-parameter was received"}), 415
    except TypeError:
        # If program cannot translate data to json or can't append list
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        # If There're other SERVER errors
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500
    # If OKAY, send data to client
    return Response(result, mimetype='application/json')


@app.route('/get_all_items', methods=['GET'])
def get_all_items():
    try:
        # Select all dishes from DB
        menu_items = Menu.query.order_by(Menu.item_id).all()
        menu_list = []
        for items in menu_items:
            # Append list by new items (json)
            menu_list.append(items.prepare_json())
        # Jsonificate result
        result = json.dumps({'menu': menu_list})
    except TypeError:
        # If program cannot translate data to json or can't append list
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        # If There're other SERVER errors
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500
    # If OKAY, send data to client
    return Response(result, mimetype='application/json')


# Sends file from the database to client
@app.route('/photos/<image>', methods=['GET'])
def get_photo(image):
    try:
        # Get first base64 object photo with name <image> from database
        photo_base64 = Images.query.filter(Images.fullname == image).first()
        # Create empty variable response
        response = None
        # If photo exists
        if photo_base64:
            # Translate base64 object to photo
            photo = base64.b16decode(photo_base64.image_base64)
            # Make response and set headers
            response = make_response(photo)
            response.headers['Content-Transfer-Encoding'] = 'base64'
            response.headers['Content-Type'] = 'image'
        # If there's no photo in db
        if not response:
            return jsonify({'code': 404, 'desc': "Not Found"}), 404
    except TypeError:
        # If program cannot translate data to json or can't append list
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        # If there're other SERVER errors
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500
    # If OKAY, send photo to client
    return response


# Sends to a client last db update (date and time)
@app.route('/check_update', methods=['GET'])
def check_update():
    try:
        # Call function of class LastUpdate
        update = LastUpdate().check_update()
        return update
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# Sends to client count of rows in Menu table
@app.route('/get_dish_count', methods=['GET'])
def get_dish_count():
    try:
        # Select count of rows in Menu
        menu_count = Menu.query.count()
        return str(menu_count)
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


#
# ############ FUNCTIONS REQUERES MODIFICATION #######
#
# I NEED TO CHANGE IT A LITTLE BIT
"""
# User authorization with create session
@app.route('/auth', methods=['POST'])
def authorize():
    if request.method == 'POST':
        # Get data and convert them to JSON
        data = request.data
        json_data = json.loads(data)
        # Select record from DB, where login=login
        auth = Auth.query.filter(Auth.email == json_data['email']).first()
        if not auth:
            return jsonify({'code': 401, 'desc': "Email incorrect"}), 401
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

"""
@app.route('/hi', methods=['GET', 'POST'])
@login_required
def hi():
    uuidstr = str(uuid.uuid4())[1:8]
    return uuidstr


# TEST METHOD - error responses
@app.route('/get_wrong/<i_id>', methods=['GET', 'POST'])
def get_wrong(i_id):
    if i_id == '200':
        return jsonify({'code': 200, 'desc': "OK"}), 200
    if i_id == '400':
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    if i_id == '415':
        return jsonify({'code': 415, 'desc': "Unsupported Media Type"}), 415
    if i_id == '500':
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# Checks correct session data
def log_required(login, unique):
    if login in session:
        if session[login] == unique:
            return True
    return False
