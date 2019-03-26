from datetime import datetime, timedelta
from app import db
from models import *


def convert_utc_now_to_moscow():
    date_time_now_utc = datetime.utcnow()
    date_time_moscow_now = date_time_now_utc + timedelta(hours=3)
    return date_time_moscow_now


def delete_old_booking():
    date_time_now = convert_utc_now_to_moscow()
    Booking.query.filter(Booking.date_time_to < date_time_now).delete()
    db.session.commit()
    return True


def delete_old_access_codes():
    date_time_now = convert_utc_now_to_moscow()
    UserRegAccessCode.query.filter(UserRegAccessCode.datetime < date_time_now).delete()
    db.session.commit()
    return True
