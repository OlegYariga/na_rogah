import uuid
import base64
import json
from hashlib import sha256
from random import randint
from datetime import timedelta, time, date

from sqlalchemy import create_engine
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
from sendmail import send_mail
from flask_security import current_user

from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                get_raw_jwt)

# Load APPLICATION_ROOT from config
def_route = '/api/v1'
expires_jwt = timedelta(minutes=10000)


# Make session permanent with lifetime=1 before request
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=300)


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
        # Select date of last TimeTable update
        timetable_update = TimeTableUpdate().check_update()
        result = jsonify({'date': update, 'count': menu_count, 'timetable_update': timetable_update})
        return result
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# Returns timetable of NaRogah
@app.route(def_route+'/timetable', methods=['GET'])
def timetable():
    try:
        # Select all timetables and sort them by ID
        timetables = Timetable.query.order_by(Timetable.timetable_id).all()
        timetable_list = []
        for timetable_item in timetables:
            # Turn items to JSON
            timetable_list.append(timetable_item.prepare_json())
        return jsonify({'data': timetable_list})
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/find_user/<user_email>', methods=['GET'])
def find_user(user_email):
    try:
        user = Users.query.filter(Users.email == str(user_email)).first()
        if user:
            return jsonify({'code': 200, 'desc': "User was found"}), 200
        return jsonify({'code': 404, 'desc': "Not Found"}), 404
    except ValueError:
        # If GET parameter was wrong
        return jsonify({'code': 415, 'desc': "Not valid was received"}), 415
    except TypeError:
        # If program cannot translate data to json or can't append list
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        # If There're other SERVER errors
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500

########################################################################################################################
########################################################################################################################
########################################################################################################################
# POST methods


# User authorization with create JWT
@app.route(def_route+'/auth', methods=['POST'])
def authorize():
    try:
        # Get data and convert them to JSON
        json_data = json.loads(request.data)
        # Select record from DB, where email==email and password==password
        passw = sha256(str(json_data['password']).encode('utf-8')).hexdigest()
        user = Users.query.filter(and_(Users.email == json_data['email'],
                                       Users.password == passw)).first()
        if user:
            # Generate token with JWT
            access_token = "Bearer "+create_access_token(identity=user.email, expires_delta=expires_jwt)
            # Create a response with access token
            return jsonify({'code': 200, 'desc': "Authorized",
                            'email': str(user.email), 'access_token': access_token}), 200
        return jsonify({'code': 401, 'desc': "Credentials incorrect"}), 401
    except KeyError:
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# Method to verify email
@app.route(def_route+'/verify_email', methods=['POST'])
def verify_email():
    try:
        # Get data and convert them to JSON (ONLY email)
        json_data = json.loads(request.data)
        # Generate unique 5-signs numeric code
        code = str(randint(10000, 99999))
        # Create service headers and message body
        subject = "'На Рогах' подтверждение E-mail"
        recipient = json_data['email']
        body = 'Добро пожаловать в ресторан "На Рогах"! Ваш код подтверждения - ' + code
        # Add code to UserAccessCode
        UserRegAccessCode().insert_user_reg_access_code(email=json_data['email'], code=code)
        # Send mail
        send_mail(recipient, subject, body)
        return jsonify({'code': 200, 'desc': "Email was sent", 'email_code': code}), 200
    except KeyError:
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/test_auth', methods=['GET'])
@jwt_required
def test_auth():
    return jsonify({'code': 200, 'desc': "ok"}), 200


@app.route(def_route+'/reg_user', methods=['POST'])
def reg_user():
    try:
        # Get data and convert into JSON (email, password, code
        json_data = json.loads(request.data)
        user_accessed = UserRegAccessCode().find_user_reg_access_code(email=json_data['email'], code=json_data['code'])
        if user_accessed:
            # Select user with such email
            user_exist = Users.query.filter(Users.email == json_data['email']).first()
            # If there's such user in DB
            if not user_exist:
                passw = sha256(str(json_data['password']).encode('utf-8')).hexdigest()
                # Create user with recieved data
                user = Users(email=json_data['email'], password=passw,
                             name=json_data['name'], phone=json_data['phone'],
                             active=False)
                # Add user to DB
                db.session.add(user)
                db.session.commit()
                if user:
                    # Generate token with JWT
                    access_token = "Bearer " + create_access_token(identity=user.email, expires_delta=expires_jwt)
                    # Create a response with access token
                    return jsonify({'code': 200, 'desc': "Authorized",
                                    'email': str(user.email), 'access_token': access_token}), 200
            return jsonify({'code': 401, 'desc': "User already exists"}), 401
        return jsonify({'code': 422, 'desc': "Code incorrect"}), 422
    except KeyError:
        return jsonify({'code': 400, 'desc': "Key Error"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/password_recovery', methods=['POST'])
def password_recovery():
    try:
        # Get data and convert into JSON (email, password, code
        json_data = json.loads(request.data)
        if UserRegAccessCode().find_user_reg_access_code(email=json_data['email'], code=json_data['code']):
            # If user was registered
            user_recovery = Users.query.filter(Users.email == json_data['email']).first()
            # If code from email is correct and suxh user exists
            if user_recovery:
                passw = sha256(str(json_data['password']).encode('utf-8')).hexdigest()
                # Update password of a user with new password
                user_recovery.password = passw
                # Change record in DB
                db.session.add(user_recovery)
                db.session.commit()
                return jsonify({'code': 200, 'desc': "OK"}), 200
            return jsonify({'code': 401, 'desc': "No such user detected"}), 401
        return jsonify({'code': 422, 'desc': "Code incorrect"}), 422
    except KeyError:
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# Check if user is authorized
@app.route(def_route+'/check_auth', methods=['GET'])
@jwt_required
def check_auth():
    try:
        return jsonify({'code': 200, 'desc': "OK"}), 200
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# This view shows empty tables in chosen date-time interval
@app.route(def_route+'/empty_places', methods=['POST'])
def empty_places():
    try:
        # Get data and convert into JSON (date_from, time_from, date_to, Time_to)
        data = request.data
        json_data = json.loads(data)
        str_date_time_from = json_data['date'] + ' ' + json_data['time_from']
        str_date_time_to = json_data['date_to'] + ' ' + json_data['time_to']
        date_time_from = datetime.strptime(str_date_time_from, "%Y-%m-%d %H:%M:%S")
        date_time_to = datetime.strptime(str_date_time_to, "%Y-%m-%d %H:%M:%S")
        if date_time_from <= date_time_to:
            booking = Booking.query.filter(
                                                and_((
                                                    or_(Booking.date_time_from >= date_time_from,
                                                        Booking.date_time_to >= date_time_from)),
                                                    or_(Booking.date_time_from <= date_time_to,
                                                        Booking.date_time_to <= date_time_to))
                                                ).all()
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
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error!"}), 500


@app.route(def_route+'/reserve_place', methods=['POST'])
@jwt_required
def reserve_place():
    try:
        with lock:
            json_data = json.loads(request.data)
            if not json_data['email'] == "":
                str_date_time_from = json_data['date'] + ' ' + json_data['time_from']
                str_date_time_to = json_data['date_to'] + ' ' + json_data['time_to']
                date_time_from = datetime.strptime(str_date_time_from, "%Y-%m-%d %H:%M:%S")
                date_time_to = datetime.strptime(str_date_time_to, "%Y-%m-%d %H:%M:%S")
                if date_time_from <= date_time_to:
                    forbidden = Booking.query.with_for_update(of=Booking).\
                        filter(and_(json_data['table_id'] == Booking.table_id,
                                                        and_((
                                                            or_(Booking.date_time_from >= date_time_from,
                                                                Booking.date_time_to >= date_time_from)),
                                                            or_(Booking.date_time_from <= date_time_to,
                                                                Booking.date_time_to <= date_time_to))
                                                            )).all()
                    user = Users.query.filter(Users.email == json_data['email']).first()
                    table_id = Tables.query.filter(Tables.table_id == json_data['table_id']).first()
                    if not forbidden:
                        if table_id and user:
                            booking = Booking(date_time_from=date_time_from,
                                              date_time_to=date_time_to,
                                              user_id=user.id,
                                              table_id=json_data['table_id'])
                            db.session.add(booking)
                            db.session.commit()
                            forbidden = Booking.query.filter(and_(json_data['table_id'] == Booking.table_id,
                                                                  and_((
                                                                      or_(Booking.date_time_from >= date_time_from,
                                                                          Booking.date_time_to >= date_time_from)),
                                                                      or_(Booking.date_time_from <= date_time_to,
                                                                          Booking.date_time_to <= date_time_to))
                                                                  )).count()
                            if forbidden > 1:
                                bookeed = Booking.query.filter(Booking.booking_id == booking.booking_id).delete()
                                db.session.commit()
                                return jsonify({'code': 451, 'desc': "This time is booked"}), 451
                            return jsonify({'code': 200, 'desc': "OK"}), 200
                        return jsonify({'code': 404, 'desc': "Such table was not found"}), 404
                    return jsonify({'code': 451, 'desc': "This time is booked"}), 451
                return jsonify({'code': 400, 'desc': "Bag request - time_from > time_to"}), 400
            return jsonify({'code': 420, 'desc': "Email is empty"}), 420
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/show_user_booking', methods=['GET'])
@jwt_required
def show_user_booking():
    try:
        user_email = get_jwt_identity()
        user = Users.query.filter(Users.email == str(user_email)).first()
        if user:
            bookings = Booking.query.filter(Booking.user_id == user.id).order_by(Booking.date_time_from).all()
            booking_list = []
            for booking in bookings:
                booking_list.append(booking.prepare_json())
            return jsonify({'bookings': booking_list}), 200
        return jsonify({'code': 404, 'desc': "User not found"}), 404
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/delete_user_booking/<booking_id>', methods=['DELETE'])
@jwt_required
def delete_user_booking(booking_id):
    try:
        user_email = get_jwt_identity()
        user = Users.query.filter(Users.email == str(user_email)).first()
        if user:
            bbk = Booking.query.filter(and_(Booking.user_id == int(user.id),
                                            Booking.booking_id == int(booking_id),
                                            Booking.accepted
                                            )).all()
            bookings = Booking.query.filter(and_(Booking.user_id == int(user.id),
                                                 Booking.booking_id == int(booking_id)
                                                 )).delete()
            for booking in bbk:
                deleted_booking = DeletedBooking(date_time_from=booking.date_time_from,
                                                 date_time_to=booking.date_time_to,
                                                 user_id=user.id,
                                                 table_id=booking.table_id)
                db.session.add(deleted_booking)
            db.session.commit()
            if not bookings == 0:
                return jsonify({'code': 200, 'desc': "OK"}), 200
            return jsonify({'code': 404, 'desc': "Booking not found"}), 404
        return jsonify({'code': 404, 'desc': "User not found"}), 404
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/view_user_credentials', methods=['GET'])
@jwt_required
def view_user_credentials():
    try:
        user_email = get_jwt_identity()
        user = Users.query.filter(Users.email == str(user_email)).first()
        if user:
            return jsonify({'data': user.prepare_json()}), 200
        return jsonify({'code': 404, 'desc': "User not found"}), 404
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/change_user_credentials', methods=['PATCH'])
@jwt_required
def change_user_credentials():
    try:
        user_email = get_jwt_identity()
        json_data = json.loads(request.data)
        if not json_data['new_email'] or json_data['new_email'] == "":
            user = Users.query.filter(Users.email == str(user_email)).first()
            if not user:
                return jsonify({'code': 404, 'desc': "User not found"}), 404
            user.name = str(json_data['name'])
            user.phone = str(json_data['phone'])
            bd = json_data['birthday']
            if not bd or bd == "":
                date_birth = None
            else:
                date_birth = datetime.strptime(bd, "%Y-%m-%d")
            user.birthday = date_birth
            db.session.commit()
            return jsonify({'code': 200, 'desc': "OK"}), 200
        else:
            user_accessed = UserRegAccessCode().find_user_reg_access_code(email=json_data['new_email'],
                                                                          code=json_data['code'])
            if not user_accessed:
                return jsonify({'code': 404, 'desc': "New email verify code is not valid"}), 404
            new_user_exist = Users.query.filter(Users.email == json_data['new_email']).first()
            user = Users.query.filter(Users.email == str(user_email)).first()
            # If there's such user in DB
            if not new_user_exist and user:
                user.email = str(json_data['new_email'])
                user.name = str(json_data['name'])
                user.phone = str(json_data['phone'])
                bd = json_data['birthday']
                if not bd or bd == "":
                    date_birth = None
                else:
                    date_birth = datetime.strptime(bd, "%Y-%m-%d")
                user.birthday = date_birth
                db.session.commit()
                if user:
                    # Generate token with JWT
                    access_token = "Bearer " + create_access_token(identity=user.email, expires_delta=expires_jwt)
                    # Create a response with access token
                    return jsonify({'code': 200, 'desc': "Authorized",
                                    'email': str(user.email), 'access_token': access_token}), 200
            return jsonify({'code': 404,
                            'desc': "Current user not found or user with new_email already exists"}), 404
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# ADMIN VIEW
# View function for custom admin
@app.route(def_route+'/', methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    try:
        # If something was POSTed
        if request.method == 'POST':
            # If button "Accept" was pressed
            if request.form['index'] == "0":
                # Select id of record, where button was pressed
                booking_ident = request.form['buttonpressed']
                if booking_ident:
                    # Select record of booking with such ID
                    order_table = Booking.query.filter(Booking.booking_id == booking_ident).first()
                    # If record exists
                    if order_table:
                        # If record was not accepted yet
                        if not order_table.accepted:
                            # Change status to "Accepted" and deploy changes to DB
                            order_table.accepted = True
                            db.session.add(order_table)
                            db.session.commit()
                            # Select email of user, created booking
                            user = Users.query.filter(Users.id == order_table.user_id).first()
                            # Create service headers
                            if user:
                                mail_to = user.email
                                subject = "Ресторан 'На Рогах'"
                                # Select user's name
                                user_name = user.name
                                if not user_name:
                                    # If there's no name, create generalized greeting
                                    name = str("мы рады, что Вы пользуетесь нашим приложением")
                                else:
                                    # Else, convert name to string
                                    name = str(user_name)
                                # Select data, identifier, table's number, time_from and time_to
                                ident = str(order_table.booking_id)
                                num = str(order_table.table_id)
                                b_date = str(order_table.date_time_from.strftime('%d.%m.%Y'))
                                b_time_from = str(order_table.date_time_from.strftime('%H:%M'))
                                b_time_to = str(order_table.date_time_to.strftime('%H:%M'))
                                # Insert data to message body in HTML
                                body = """
                                <h1><b>Здравствуйте, """+name+"""!</b></h1>
                                <p>Вы успешно забронировали стол <b>№ """ +\
                                       num+"""</b> на <b>""" +\
                                       b_date+"""</b> с <b>""" +\
                                       b_time_from+"""</b> до <b>""" +\
                                       b_time_to+"""</b>. Номер Вашего заказа - <b>"""\
                                       + ident + """</b></p>
                                <p>Мы с радостью ждем Вас в гости!</p>
                                """
                                # Send email
                                send_mail(mail_to, subject, body)
            # If was pressed 'delete' button
            if request.form['index'] == "1":
                # Select id of record, where button was pressed
                booking_delete = request.form['booking_delete']
                if booking_delete:
                    # Delete such record from DB. If there's no records - do nothing
                    Booking.query.filter(Booking.booking_id == booking_delete).delete()
                    db.session.commit()
        # MAIN PART
        # Select not-accepted booking records from DB
        booking = Booking.query.filter(not_(Booking.accepted == True)).all()

        flights_keys = {}
        flights = []
        for order in booking:
            date_from = datetime.strftime(order.date_time_from, "%d.%m.%Y")
            time_from = datetime.strftime(order.date_time_from, "%H:%M")
            date_to = datetime.strftime(order.date_time_to, "%d.%m.%Y")
            time_to = datetime.strftime(order.date_time_to, "%H:%M")
            # Select users in every booking item (order)
            user = Users.query.filter(Users.id == order.user_id).first()
            # Fill th dictionary with booking and user data
            flights_keys['booking_id'] = order.booking_id
            flights_keys['date_from'] = date_from
            flights_keys['time_from'] = time_from
            flights_keys['time_to'] = time_to
            if user:
                flights_keys['user_name'] = user.name
                flights_keys['phone'] = user.phone
            else:
                flights_keys['user_name'] = "Нет данных"
                flights_keys['phone'] = "Нет данных"
            flights_keys['table_id'] = order.table_id
            # Append list with the dictionary and clear dictionary
            flights.append(flights_keys)
            flights_keys = {}
        # Create view page with data
        return render_template('index.html', flights=flights)
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route("/view_booking", methods=['GET', 'POST'])
@login_required
def view_booking():
    try:
        date_booking = None
        date_booking_date = None
        # If something was POSTed
        if request.method == 'POST':
            # If button "Accept" was pressed
            if request.form['index'] == "0":
                # Select id of record, where button was pressed
                date_booking = request.form['date_booking']
            # If was pressed 'delete' button
            if request.form['index'] == "1":
                date_booking = request.form['del_date']
                # Select id of record, where button was pressed
                booking_delete = request.form['booking_delete']
                if booking_delete:
                    # Delete such record from DB. If there's no records - do nothing
                    Booking.query.filter(Booking.booking_id == booking_delete).delete()
                    db.session.commit()
            if request.form['index'] == "10":
                date_booking = request.form['del_date']
                # Select id of record, where button was pressed
                booking_delete = request.form['deleted_booking_confirm']
                if booking_delete:
                    # Delete such record from DB. If there's no records - do nothing
                    DeletedBooking.query.filter(DeletedBooking.booking_id == booking_delete).delete()
                    db.session.commit()
        if request.method == 'GET':
            date_time_now_utc = datetime.utcnow()
            date_time_moscow_now = date_time_now_utc + timedelta(hours=3)
            date_time_moscow_now = datetime.strftime(date_time_moscow_now, "%Y-%m-%d")
            date_booking = str(date_time_moscow_now)
        # MAIN PART
        booking = Booking.query.filter((Booking.accepted == True)).all()
        deleted_booking = DeletedBooking.query.all()
        del_book_keys = {}
        del_book_list = []

        for del_book in deleted_booking:
            #print(del_book)
            date_from = datetime.strftime(del_book.date_time_from, "%d.%m.%Y")
            time_from = datetime.strftime(del_book.date_time_from, "%H:%M")
            date_to = datetime.strftime(del_book.date_time_to, "%d.%m.%Y")
            time_to = datetime.strftime(del_book.date_time_to, "%H:%M")
            if date_booking:
                date_booking_str = datetime.strptime(date_booking, "%Y-%m-%d")
                date_booking_date = datetime.strftime(date_booking_str, "%d.%m.%Y")
            if date_booking_date:
                if date_from == date_booking_date:
                    user = Users.query.filter(Users.id == del_book.user_id).first()
                    del_book_keys['user_name'] = user.name
                    del_book_keys['user_phone'] = user.phone

                    del_book_keys['booking_id'] = del_book.booking_id
                    del_book_keys['date_from'] = date_from
                    del_book_keys['time_from'] = time_from
                    del_book_keys['time_to'] = time_to
                    del_book_keys['table_id'] = del_book.table_id
                    del_book_list.append(del_book_keys)
                    del_book_keys = {}

        flights_keys = {}
        flights = []
        for order in booking:
            date_from = datetime.strftime(order.date_time_from, "%d.%m.%Y")
            time_from = datetime.strftime(order.date_time_from, "%H:%M")
            date_to = datetime.strftime(order.date_time_to, "%d.%m.%Y")
            time_to = datetime.strftime(order.date_time_to, "%H:%M")
            if date_booking:
                date_booking_str = datetime.strptime(date_booking, "%Y-%m-%d")
                date_booking_date = datetime.strftime(date_booking_str, "%d.%m.%Y")
            if date_booking_date:
                if date_from == date_booking_date:
                    # Select users in every booking item (order)
                    user = Users.query.filter(Users.id == order.user_id).first()
                    # Fill th dictionary with booking and user data
                    flights_keys['booking_id'] = order.booking_id
                    flights_keys['date_from'] = date_from
                    flights_keys['time_from'] = time_from
                    flights_keys['time_to'] = time_to
                    if user:
                        flights_keys['user_name'] = user.name
                        flights_keys['phone'] = user.phone
                    else:
                        flights_keys['user_name'] = "Нет данных"
                        flights_keys['phone'] = "Нет данных"
                    flights_keys['table_id'] = order.table_id
                    # Append list with the dictionary and clear dictionary
                    flights.append(flights_keys)
                    flights_keys = {}
        date = date_booking
        return render_template('view_booking.html', flights=flights, date=date, del_book_list=del_book_list)
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route("/reg_booking", methods=['GET', 'POST'])
@login_required
def reg_booking():
    try:
        # variable to store errors, if they are and 0, if there're no errors
        ans = 3
        # If something was POSTed
        if request.method == 'POST':
            name = request.form['inputName']
            phone = request.form['InputPhone']
            date_from = request.form['InputDateFrom']
            time_hours_from = request.form['InputTimeHoursFrom']
            time_minutes_from = request.form['InputTimeMinutesFrom']
            time_hours_to = request.form['InputTimeHoursTo']
            time_minutes_to = request.form['InputTimeMinutesTo']
            date_to = request.form['InputDateTo']
            table = request.form['InputTableNum']

            date_time_from = str(date_from) + " " + str(time_hours_from) + ":" + str(time_minutes_from)
            date_time_to = str(date_to) + " " + str(time_hours_to) + ":" + str(time_minutes_to)
            if (datetime.strptime(date_time_to,
                                  "%Y-%m-%d %H:%M") - datetime.strptime(date_time_from,
                                                                        "%Y-%m-%d %H:%M")) <= timedelta(hours=4):
                if datetime.strptime(date_time_from, "%Y-%m-%d %H:%M") < datetime.strptime(date_time_to, "%Y-%m-%d %H:%M"):

                    booking_week_day = datetime.strptime(date_time_from, "%Y-%m-%d %H:%M").weekday()
                    timetable = None
                    if booking_week_day == 0:
                        timetable = Timetable.query.filter(Timetable.week_day == "пн").first()
                    elif booking_week_day == 1:
                        timetable = Timetable.query.filter(Timetable.week_day == "вт").first()
                    elif booking_week_day == 2:
                        timetable = Timetable.query.filter(Timetable.week_day == "ср").first()
                    elif booking_week_day == 3:
                        timetable = Timetable.query.filter(Timetable.week_day == "чт").first()
                    elif booking_week_day == 4:
                        timetable = Timetable.query.filter(Timetable.week_day == "пт").first()
                    elif booking_week_day == 5:
                        timetable = Timetable.query.filter(Timetable.week_day == "сб").first()
                    elif booking_week_day == 6:
                        timetable = Timetable.query.filter(Timetable.week_day == "вс").first()
                    if timetable:
                        str_date_time_from = datetime.strptime(date_time_from, "%Y-%m-%d %H:%M").time()
                        str_date_time_to = datetime.strptime(date_time_to, "%Y-%m-%d %H:%M").time()
                        print("Время начала из формы: ", str_date_time_from)
                        print("Время окончания из формы: ", str_date_time_to)
                        print("Время начала из расписания: ", timetable.time_from)
                        print("Время окончания из расписания: ", timetable.time_to)
                        if str_date_time_from >= timetable.time_from:
                            forbidden = Booking.query.filter(and_(table == Booking.table_id,
                                                                  and_((
                                                                      or_(Booking.date_time_from >= date_time_from,
                                                                          Booking.date_time_to >= date_time_from)),
                                                                      or_(Booking.date_time_from <= date_time_to,
                                                                          Booking.date_time_to <= date_time_to))
                                                                  )).all()
                            if not forbidden:

                                email = str(uuid.uuid4())+"@mail.ru"
                                password = email
                                user = Users(email=email, password=password, name=name, phone=phone)
                                db.session.add(user)
                                db.session.commit()
                                user = Users.query.filter(Users.email == email).first()
                                is_table = Tables.query.filter(Tables.table_id == table).first()

                                if user and is_table:
                                    booking = Booking(date_time_from=date_time_from,
                                                      date_time_to=date_time_to,
                                                      user_id=user.id,
                                                      table_id=table, accepted=True)
                                    db.session.add(booking)
                                    db.session.commit()
                                    ans = 0
                                else:
                                    ans = 1
                            else:
                                ans = 4
                        else:
                           ans = 5
                    else:
                        ans = 5
                else:
                    ans = 2
            else:
                ans = 6

        return render_template('reg_booking.html', ans=ans)
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route("/reg_new_admin", methods=['GET', 'POST'])
@login_required
def reg_new_admin():
    try:
        if current_user.has_role("admin"):
            if request.method == 'POST':
                name = request.form['inputName']
                phone = request.form['InputPhone']
                email = request.form['InputEmail']
                password = request.form['InputPassword']
                password_agane = request.form['InputPasswordAgane']

                if password == password_agane:
                    is_user = Users.query.filter(Users.email == str(email)).first()
                    if not is_user:
                        new_user = Users(email=email, password=password, name=name, phone=phone, active=True)
                        db.session.add(new_user)
                        db.session.commit()
                        return render_template('reg_new_admin.html', ans=1, access=True)
                    return render_template('reg_new_admin.html', ans=2, access=True)
                return render_template('reg_new_admin.html', ans=3, access=True)
            return render_template('reg_new_admin.html', access=True)
        else:
            return render_template('reg_new_admin.html', access=False)
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500
