import uuid
import base64
import json
from random import randint
from datetime import timedelta, time, date

from flask import request, jsonify, session, Response, make_response, send_from_directory, render_template
from flask_security import login_required
from flask_mail import Message
from sqlalchemy import and_, or_, not_
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
    try:
        # Select menu from DB where Category.category_id == <class_id>
        menu = Menu.query.filter(Menu.category_id == int(class_id)).order_by(Menu.name).all()
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
    try:
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
    except KeyError:
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/reg_user', methods=['POST'])
def reg_user():
    try:
        # Get data and convert into JSON (email, password, code
        data = request.data
        json_data = json.loads(data)
        # ADD EMAIL FOR TESTING!!!
        #session[json_data['email']] = '10000'
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
            return jsonify({'code': 400, 'desc': "Error when codes compare with each other"}), 400
        return jsonify({'code': 400, 'desc': "Error in key 'email'"}), 400
    except KeyError:
        return jsonify({'code': 400, 'desc': "Key Error"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/password_recovery', methods=['POST'])
def password_recovery():
    try:
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
    except KeyError:
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


#### Протестировать!!!
@app.route(def_route+'/empty_places', methods=['POST'])
def empty_places():
    try:
        data = request.data
        json_data = json.loads(data)
        #if (json_data['email'] in session) and (str(json_data['code']) == str(session[json_data['email']])):
        if datetime.strptime(json_data['time_from'], "%H:%M:%S") <= datetime.strptime(json_data['time_to'], "%H:%M:%S"):
            booking = Booking.query.filter(and_(json_data['date'] == Booking.date,
                                                and_((
                                                    or_(Booking.time_from >= json_data['time_from'],
                                                        Booking.time_to >= json_data['time_from'])),
                                                    or_(Booking.time_from <= json_data['time_to'],
                                                        Booking.time_to <= json_data['time_to']))
                                                )).all()
            tables = Tables.query.all()

            table_list = []
            for table in tables:
                table_list.append(table)

            for table in tables:
                for order in booking:
                    if (table.table_id == order.table_id) and (table in table_list):
                        table_list.remove(table)
            response_list = []
            for l_table in table_list:
                response_list.append(l_table.prepare_json())

            return jsonify({'data': response_list}), 200
        return jsonify({'code': 400, 'desc': "Bag request - time_from > time_to"}), 400
        #return jsonify({'code': 400, 'desc': "Code incorrect. Repeat sending"}), 400
    except KeyError:
        return jsonify({'code': 400, 'desc': "Key error"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error!"}), 500


@app.route(def_route+'/reserve_place', methods=['POST'])
def reserve_place():
    try:
        data = request.data
        json_data = json.loads(data)
        #########################
        ########################
        # Этот код был перенесен из эндпоинта reg_user
        user_exist = Users.query.filter(Users.email == json_data['email']).first()
        if not user_exist:
            user = Users(email=json_data['email'], password="0000",
                         name=json_data['name'], phone=json_data['phone'],
                         active=False)
            db.session.add(user)
            db.session.commit()
        ########################
        ########################

        #if (json_data['email'] in session) and (str(json_data['code']) == str(session[json_data['email']])):
        if datetime.strptime(json_data['time_from'], "%H:%M:%S") <= datetime.strptime(json_data['time_to'], "%H:%M:%S"):
            forbidden = Booking.query.filter(and_(json_data['date'] == Booking.date, json_data['table_id']== Booking.table_id,
                                                and_((
                                                    or_(Booking.time_from >= json_data['time_from'],
                                                        Booking.time_to >= json_data['time_from'])),
                                                    or_(Booking.time_from <= json_data['time_to'],
                                                        Booking.time_to <= json_data['time_to']))
                                                )).all()
            user = Users.query.filter(Users.email == json_data['email']).first()
            table_id = Tables.query.filter(Tables.table_id == json_data['table_id']).first()
            if not forbidden:
                if table_id:
                    booking = Booking(date=json_data['date'],
                                      time_from=json_data['time_from'],
                                      time_to=json_data['time_to'],
                                      user_id=user.id,
                                      table_id=json_data['table_id'])
                    db.session.add(booking)
                    db.session.commit()
                    return jsonify({'code': 200, 'desc': "OK"}), 200
                return jsonify({'code': 404, 'desc': "Such table was not found"}), 404
            return jsonify({'code': 451, 'desc': "This time is booked"}), 451
        return jsonify({'code': 400, 'desc': "Bag request - time_from > time_to"}), 400
        #return jsonify({'code': 401, 'desc': "Unauthorized"}), 401
    except KeyError:
        return jsonify({'code': 400, 'desc': "Key error"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/reservation')
def reservation():
    flights = Booking.query.all()
    return render_template('index.html', flights=flights)


# НУЖНО ДОДЕЛАТЬ
@app.route(def_route+'/', methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if request.form['index'] == "0":
            booking_ident = request.form['buttonpressed']
            if booking_ident:
                order_table = Booking.query.filter(Booking.booking_id == booking_ident).first()
                if order_table:
                    if not order_table.accepted:
                        order_table.accepted = True
                        db.session.add(order_table)
                        db.session.commit()
                        user = Users.query.filter(Users.id == order_table.user_id).first()
                        mail_to = user.email
                        subject = "Ресторан 'На Рогах'"
                        body = "Бронирование прошло успешно!\n " \
                               "Номер Вашей брони - "+str(order_table.booking_id)+"\n " \
                               "Стол № "+str(order_table.table_id)+"\n " \
                               "Дата: "+str(order_table.date)+"\n " \
                               "Время начала: "+str(order_table.time_from)+"\n " \
                               "Время окончания: "+str(order_table.time_to)
                        send_mail(mail_to, subject, body)

        if request.form['index'] == "1":
            booking_delete = request.form['booking_delete']
            if booking_delete:
                Booking.query.filter(Booking.booking_id == booking_delete).delete()
                db.session.commit()
    # filter(Booking.date == datetime.now().date())
    booking = Booking.query.filter(not_(Booking.accepted==True)).all()
    flights_keys = {}
    flights = []
    for order in booking:
        user = Users.query.filter(Users.id == order.user_id).first()
        flights_keys['booking_id'] = order.booking_id
        flights_keys['date'] = order.date
        flights_keys['time_from'] = order.time_from
        flights_keys['time_to'] = order.time_to
        if user:
            flights_keys['user_name'] = user.name
            flights_keys['phone'] = user.phone
        else:
            flights_keys['user_name'] = "Нет данных"
            flights_keys['phone'] = "Нет данных"
        flights_keys['table_id'] = order.table_id

        flights.append(flights_keys)
        flights_keys = {}

    return render_template('index.html', flights=flights)


def send_mail(mail_to, subject, text):
    msg = Message()
    msg.subject = subject
    msg.recipients = [mail_to]
    msg.body = text
    mail.send(msg)

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
