import uuid
import base64
import json
from random import randint
from datetime import timedelta

from flask import request, jsonify, session, Response, make_response, send_from_directory
from flask_security import login_required
from flask_mail import Message
from sqlalchemy import and_, or_
from werkzeug import secure_filename

from models import Users
from models import LastUpdate
from models import Category, Menu, Images
from app import *
from app import mail

# Load APPLICATION_ROOT from config
def_route = '/api/v1'

# Make session permanent with lifetime=1 before request
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


# Returns all dish categories (in array)
@app.route(def_route+'/categories', methods=['GET'])
def get_classes():
    try:
        # Select categories from DB
        food_class = Category.query.order_by(Category.category_id).all()
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
@app.route(def_route+'/menu/<class_id>', methods=['GET'])
def get_menu(class_id):
    #try:
        # Select menu from DB where Category.category_id == <class_id>
        menu = Menu.query.filter(Menu.category_id == int(class_id)).order_by(Menu.name).all()
        # Create empty list
        menu_list = []
        for items in menu:
            # Append list by new items (json)
            menu_list.append(items.prepare_json())
        # Jsonificate result
        result = json.dumps({'menu': menu_list})
    #except ValueError:
        # If GET parameter was wrong
        #return jsonify({'code': 415, 'desc': "Not int-parameter was received"}), 415
    #except TypeError:
        # If program cannot translate data to json or can't append list
        #return jsonify({'code': 400, 'desc': "Bad request"}), 400
    #except Exception:
        # If There're other SERVER errors
        #return jsonify({'code': 500, 'desc': "Internal server error"}), 500
    # If OKAY, send data to client
        return Response(result, mimetype='application/json')


@app.route(def_route+'/get_all_items', methods=['GET'])
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


@app.route(def_route+'/menu_by_classes', methods=['GET'])
def get_menu_by_classes():
    try:
        # Select all dishes from DB
        class_items = Category.query.order_by(Category.order).all()
        class_list = []
        for items in class_items:
            # Append list by new items (json)
            class_list.append(json.loads(items.prepare_menu_items_json()))
        # Jsonificate result
        result = json.dumps({'categories': class_list})
    except TypeError:
        # If program cannot translate data to json or can't append list
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        # If There're other SERVER errors
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500
    # If OKAY, send data to client
    return Response(result, mimetype='application/json')


# Sends file from the database to client
@app.route(def_route+'/photos/<image>', methods=['GET'])
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
@app.route(def_route+'/check_update', methods=['GET'])
def check_update():
    try:
        # Call function of class LastUpdate
        update = LastUpdate().check_update()
        menu_count = Menu.query.count()
        result = jsonify({'date': update, 'count': menu_count})
        return result
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# User authorization with create session
@app.route(def_route+'/auth', methods=['POST'])
def authorize():
    try:
        # Get data and convert them to JSON
        data = request.data
        json_data = json.loads(data)
        # Select record from DB, where email==email and password==password
        user = Users.query.filter(and_(Users.email == json_data['email'],
                                       Users.password == json_data['password'])).first()
        if user:
            # Generate unique identifier
            unique = str(uuid.uuid4())
            # Create new session with key <login> and unique value
            session[str(user.email)] = unique
            # Create a response
            return jsonify({'code': 200, 'desc': "Authorized",
                            'email': str(user.email), 'uuid': unique}), 200
        return jsonify({'code': 401, 'desc': "Credentials incorrect"}), 401
    except KeyError:
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/verify_email', methods=['POST'])
def verify_email():
    # Get data and convert them to JSON (ONLY email)
    data = request.data
    json_data = json.loads(data)
    code = str(randint(10000, 99999))
    msg = Message()
    msg.subject = 'Na-Rogah verify e-mail'
    msg.recipients = [json_data['email']]
    msg.body = 'Добро пожаловать в ресторан "На Рогах"! Ваш код подтверждения - ' + code
    mail.send(msg)
    session[str(json_data['email'])] = str(code)
    return jsonify({'code': 200, 'desc': "Email was sent"}), 200


@app.route(def_route+'/reg_user', methods=['POST'])
def reg_user():
    # Get data and convert into JSON (email, password, code
    data = request.data
    json_data = json.loads(data)
    if json_data['email'] in session:
        if str(json_data['code']) == str(session[json_data['email']]):
            user_exist = Users.query.filter(Users.email == json_data['email']).first()
            if not user_exist:
                user = Users(email=json_data['email'], password=json_data['password'],
                             name=json_data['name'], surname=json_data['surname'],
                             birthday=json_data['birthday'], phone=json_data['phone'],
                             active=False)
                db.session.add(user)
                db.session.commit()
                return jsonify({'code': 200, 'desc': "OK"}), 200
            return jsonify({'code': 401, 'desc': "User already exists"}), 401
    return jsonify({'code': 400, 'desc': "Code incorrect. Repeat sending"}), 400


@app.route(def_route+'/password_recovery', methods=['POST'])
def password_recovery():
    data = request.data
    json_data = json.loads(data)
    if json_data['email'] in session:
        user_recovery = Users.query.filter(Users.email == json_data['email']).first()
        if str(json_data['code']) == str(session[json_data['email']]) and user_recovery:
            user_recovery.password = json_data['password']
            db.session.add(user_recovery)
            db.session.commit()
            return jsonify({'code': 200, 'desc': "OK"}), 200
        return jsonify({'code': 401, 'desc': "No such user detected"}), 401
    return jsonify({'code': 400, 'desc': "Code incorrect. Repeat sending"}), 400


#
# ############ FUNCTIONS REQUERES MODIFICATION #######
#
# I NEED TO CHANGE IT A LITTLE BIT


@app.route(def_route+'/hi', methods=['GET', 'POST'])
def hi():
    msg = Message(subject='Helo!', recipients=['yarigaoleg@mail.ru'], body='We need to helo U')
    mail.send(msg)
    uuidstr = str(uuid.uuid4())[1:8]
    return uuidstr


# TEST METHOD - error responses
@app.route(def_route+'/get_wrong/<i_id>', methods=['GET', 'POST'])
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
