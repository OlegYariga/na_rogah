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


# Method to verify email
@app.route(def_route+'/verify_email', methods=['POST'])
def verify_email():
    try:
        # Get data and convert them to JSON (ONLY email)
        data = request.data
        json_data = json.loads(data)
        # Generate unique 5-signs numeric code
        code = str(randint(10000, 99999))
        # Create service headers and message body
        subject = "'На Рогах' подтверждение E-mail"
        recipient = json_data['email']
        body = 'Добро пожаловать в ресторан "На Рогах"! Ваш код подтверждения - ' + code
        # Send mail
        send_mail(recipient, subject, body)
        # Created session with key <email> and value <code>
        sign_in_data = request.get_json()
        session[sign_in_data['email']] = str(code)
        print(session[sign_in_data['email']])

        #session[str(json_data['email'])] = str(code)
        for ses in session.items():
            print(ses, '   ', session[(str(json_data['email']))])
        print("\n \n \n \n \n ")
        print('email from json:::::' + str(json_data['email']))
        print('code in session::::' + str(session[json_data['email']]))
        print("\n \n \n \n \n ")
        return jsonify({'code': 200, 'desc': "Email was sent", 'email_code': code}), 200
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
        for ses in session.items():
            print(ses)
        print("\n \n \n \n \n ")
        print('email from json:::::' + str(json_data['email']))
        print('code in session::::' + str(session.get(str(json_data['email']))))
        print("\n \n \n \n \n ")
        if str(json_data['email']) in session:
            # If code from email is correct
            if str(json_data['code']) == str(session[json_data['email']]):
                user_exist = Users.query.filter(Users.email == json_data['email']).first()
                # If there's such user in DB
                if not user_exist:
                    # Create user with recieved data
                    user = Users(email=json_data['email'], password=json_data['password'],
                                 name=json_data['name'], phone=json_data['phone'],
                                 active=False)
                    # Add user to DB
                    db.session.add(user)
                    db.session.commit()
                    if user:
                        # Generate unique identifier
                        unique = str(uuid.uuid4())
                        # Create new session with key <login> and unique value
                        session[str(user.email)] = unique
                        # Create a response

                        return jsonify({'code': 200, 'desc': "OK",
                                        'email': str(user.email), 'uuid': unique}), 200
                return jsonify({'code': 401, 'desc': "User already exists"}), 401
            return jsonify({'code': 400, 'desc': "Error when codes compare with each other"}), 400
        return jsonify({'code': 400, 'desc': "Error in key 'email' or code incorrect"}), 400
    except KeyError:
        return jsonify({'code': 400, 'desc': "Key Error"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/password_recovery', methods=['POST'])
def password_recovery():
    try:
        # Get data and convert into JSON (email, password, code
        data = request.data
        json_data = json.loads(data)
        # If user is in session
        if json_data['email'] in session:
            # If user was registered
            user_recovery = Users.query.filter(Users.email == json_data['email']).first()
            # If code from email is correct and suxh user exists
            if str(json_data['code']) == str(session[json_data['email']]) and user_recovery:
                # Update password of a user with new password
                user_recovery.password = json_data['password']
                # Change record in DB
                db.session.add(user_recovery)
                db.session.commit()
                return jsonify({'code': 200, 'desc': "OK"}), 200
            return jsonify({'code': 401, 'desc': "No such user detected"}), 401
        return jsonify({'code': 400, 'desc': "Code incorrect. Repeat sending"}), 400
    except KeyError:
        return jsonify({'code': 400, 'desc': "Bad request"}), 400
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


# Check if user is authorized
@app.route(def_route+'/check_auth', methods=['POST'])
def check_auth():
    try:
        # Get data and turn them to json
        data = request.data
        json_data = json.loads(data)
        # Check if user is in sesion and uuid is correct
        if (json_data['email'] in session) and (str(json_data['uuid']) == str(session[json_data['email']])):
            return jsonify({'code': 200, 'desc': "OK"}), 200
        return jsonify({'code': 401, 'desc': "Unauthorized"}), 401
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
        #if (json_data['email'] in session) and (str(json_data['uuid']) == str(session[json_data['email']])):
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
        #return jsonify({'code': 401, 'desc': "Unauthorized"}), 401
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
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

        #if (json_data['email'] in session) and (str(json_data['uuid']) == str(session[json_data['email']])):
        if not json_data['email'] == "":
            str_date_time_from = json_data['date'] + ' ' + json_data['time_from']
            str_date_time_to = json_data['date_to'] + ' ' + json_data['time_to']
            date_time_from = datetime.strptime(str_date_time_from, "%Y-%m-%d %H:%M:%S")
            date_time_to = datetime.strptime(str_date_time_to, "%Y-%m-%d %H:%M:%S")
            if date_time_from <= date_time_to:
                forbidden = Booking.query.filter(and_(json_data['table_id'] == Booking.table_id,
                                                    and_((
                                                        or_(Booking.date_time_from >= date_time_from,
                                                            Booking.date_time_to >= date_time_from)),
                                                        or_(Booking.date_time_from <= date_time_to,
                                                            Booking.date_time_to <= date_time_to))
                                                    )).all()
                user = Users.query.filter(Users.email == json_data['email']).first()
                table_id = Tables.query.filter(Tables.table_id == json_data['table_id']).first()
                if not forbidden:
                    if table_id:
                        booking = Booking(date_time_from=date_time_from,
                                          date_time_to=date_time_to,
                                          user_id=user.id,
                                          table_id=json_data['table_id'])
                        db.session.add(booking)
                        db.session.commit()
                        return jsonify({'code': 200, 'desc': "OK"}), 200
                    return jsonify({'code': 404, 'desc': "Such table was not found"}), 404
                return jsonify({'code': 451, 'desc': "This time is booked"}), 451
            return jsonify({'code': 400, 'desc': "Bag request - time_from > time_to"}), 400
        return jsonify({'code': 420, 'desc': "Email is empty"}), 420
        #return jsonify({'code': 401, 'desc': "Unauthorized"}), 401
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/show_user_booking', methods=['POST'])
def show_user_booking():
    try:
        data = request.data
        json_data = json.loads(data)
        if (json_data['email'] in session) and (str(json_data['uuid']) == str(session[json_data['email']])):
            user = Users.query.filter(Users.email == str(json_data['email'])).first()
            if user:
                bookings = Booking.query.filter(Booking.user_id == user.id).order_by(Booking.date_time_from).all()
                booking_list = []
                for booking in bookings:
                    booking_list.append(booking.prepare_json())
                return jsonify({'bookings': booking_list}), 200
            return jsonify({'code': 404, 'desc': "User not found"}), 404
        return jsonify({'code': 401, 'desc': "Unauthorized"}), 401
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/delete_user_booking', methods=['POST'])
def delete_user_booking():
    try:
        data = request.data
        json_data = json.loads(data)
        if (json_data['email'] in session) and (str(json_data['uuid']) == str(session[json_data['email']])):
            user = Users.query.filter(Users.email == str(json_data['email'])).first()
            if user:
                bookings = Booking.query.filter(and_(Booking.user_id == int(user.id),
                                                     Booking.booking_id == int(json_data['booking_id'])
                                                     )).delete()
                db.session.commit()
                if not bookings == 0:
                    return jsonify({'code': 200, 'desc': "OK"}), 200
            return jsonify({'code': 404, 'desc': "User or booking not found"}), 404
        return jsonify({'code': 401, 'desc': "Unauthorized"}), 401
    except KeyError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except ValueError:
        return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    except Exception:
        return jsonify({'code': 500, 'desc': "Internal server error"}), 500


@app.route(def_route+'/view_user_credentials', methods=['POST'])
def view_user_credentials():
    data = request.data
    json_data = json.loads(data)
    if (json_data['email'] in session) and (str(json_data['uuid']) == str(session[json_data['email']])):
        user = Users.query.filter(Users.email == str(json_data['email'])).first()
        if user:
            return jsonify({'data': user.prepare_json()}), 200
        return jsonify({'code': 404, 'desc': "User not found"}), 404
    return jsonify({'code': 401, 'desc': "Unauthorized"}), 401


@app.route(def_route+'/change_user_credentials', methods=['POST'])
def change_user_credentials():
    data = request.data
    json_data = json.loads(data)
    if (json_data['email'] in session) and (str(json_data['uuid']) == str(session[json_data['email']])):
        if not json_data['new_email'] or json_data['new_email'] == "":
                user = Users.query.filter(Users.email == str(json_data['email'])).first()
                if user:
                    user.name = str(json_data['name'])
                    user.phone = str(json_data['phone'])
                    db.session.commit()
                    return jsonify({'code': 200, 'desc': "OK"}), 200
                return jsonify({'code': 404, 'desc': "User not found"}), 404
        else:
            if str(json_data['new_email']) in session:
                # If code from email is correct
                if str(json_data['code']) == str(session[json_data['new_email']]):
                    new_user_exist = Users.query.filter(Users.email == json_data['new_email']).first()
                    user = Users.query.filter(Users.email == str(json_data['email'])).first()
                    # If there's such user in DB
                    if not new_user_exist and user:
                        user.email = str(json_data['new_email'])
                        user.name = str(json_data['name'])
                        db.session.commit()
                        session.pop(str(json_data['email']))
                        if user:
                            # Generate unique identifier
                            unique = str(uuid.uuid4())
                            # Create new session with key <login> and unique value
                            session[str(user.email)] = unique
                            # Create a response
                            return jsonify({'code': 200, 'desc': "OK",
                                            'email': str(user.email), 'uuid': unique}), 200
                    return jsonify({'code': 404, 'desc': "Current user not found or user with new_email already exists"}), 404
                return jsonify({'code': 404, 'desc': "New email verify code is not valid"}), 404
            return jsonify({'code': 404, 'desc': "New user email was not accepted yet (use /verify_email endpoint)"}), 404
    return jsonify({'code': 401, 'desc': "Unauthorized"}), 401


#######################################################################################
# ADMIN VIEW
# View function for custom admin
@app.route(def_route+'/', methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    #try:
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
                            <p>Вы успешно забронировали стол <b>№ """+num+"""</b> на <b>"""+b_date+"""</b> с <b>"""+b_time_from+"""</b> до <b>"""+b_time_to+"""</b>. Номер Вашего заказа - <b>"""+ident+"""</b></p>
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
    #except KeyError:
        #return jsonify({'code': 406, 'desc': "Not acceptable - Key or value error"}), 406
    #except Exception:
        #return jsonify({'code': 500, 'desc': "Internal server error"}), 500



@app.route("/view_booking", methods=['GET', 'POST'])
@login_required
def view_booking():
    # try:
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
            # Select id of record, where button was pressed
            booking_delete = request.form['booking_delete']
            if booking_delete:
                # Delete such record from DB. If there's no records - do nothing
                Booking.query.filter(Booking.booking_id == booking_delete).delete()
                db.session.commit()
    if request.method == 'GET':
        date_time_now_utc = datetime.utcnow()
        date_time_moscow_now = date_time_now_utc + timedelta(hours=3)
        date_time_moscow_now = datetime.strftime(date_time_moscow_now, "%Y-%m-%d")
        date_booking = str(date_time_moscow_now)
    # MAIN PART
    booking = Booking.query.filter((Booking.accepted == True)).all()

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

    return render_template('view_booking.html', flights=flights)







# Function to send email
def send_mail(mail_to, subject, text):
    try:
        # Try to send message to user
        msg = Message()
        msg.subject = subject
        msg.recipients = [mail_to]
        msg.html = text
        mail.send(msg)
        return True
    # If in email was detected not-ascii symbols
    except UnicodeEncodeError:
        return False
    except Exception:
        return False


#
# ############ FUNCTIONS REQUERES MODIFICATION #######
#
# I NEED TO CHANGE IT A LITTLE BIT


# Checks correct session data
def log_required(login, unique):
    if login in session:
        if session[login] == unique:
            return True
    return False
