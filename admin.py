from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask import redirect, url_for
from flask_admin import AdminIndexView
from wtforms import validators
from sqlalchemy import and_
from models import *


# Create class, defining access roles and redirect to login page
class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


# Create class our AdminView
class BaseModelView(AdminMixin, ModelView):
    pass


# Class get access for admin index page
class HomeAdminView(AdminMixin, AdminIndexView):
    pass


# Create class MenuAdminView for Menu
class MenuAdminView(BaseModelView):
    # Add extra field for uploading image
    form_extra_fields = {
        'file': FileField('Изображение')
    }
    # Add necessary fields ( because we need to hide 'photo' field
    form_columns = ['Category', 'name', 'price', 'desc_short', 'desc_long', 'weight',
                    'recommended', 'file']
    column_list = ['item_id', 'name', 'price', 'desc_short', 'desc_long', 'weight',
                   'recommended', 'photo', 'Category']
    column_labels = dict(item_id='Идентификатор', name='Название блюда', price='Цена', desc_short='Краткое описание',
                         desc_long='Подробное опиасание', weight='Вес',
                         recommended='Рекоменд. блюда', photo='URL фотографии', Category='Категория')

    def on_model_change(self, form, model, is_created):
        item_name = request.form['name']
        # model.name = item_name.capitalize()
        return super(MenuAdminView, self).on_model_change(form, model, is_created)

    # Upload image to DB after model changed
    def after_model_change(self, form, model, is_created):
        model.load_image()
        # Update LastUpdate in Db
        LastUpdate().update_db()
        return super(MenuAdminView, self).on_model_change(form, model, is_created)

    # Delete all images, connected with current model
    def on_model_delete(self, model):
        model.delete_image()
        # Update LastUpdate in Db
        LastUpdate().update_db()
        return super(MenuAdminView, self).on_model_delete(model)


class CategoryAdminView(BaseModelView):
    column_labels = dict(order='Порядок категории в списке', name='Название категории')
    form_args = dict(
        menu=dict(label='Блюда в категории'),
        order=dict(label='Порядок категории в списке', validators=[validators.DataRequired()])
    )

    def on_model_change(self, form, model, is_created):
        class_name = request.form['name']
        model.name = class_name.upper()
        return super(CategoryAdminView, self).on_model_change(form, model, is_created)

    def after_model_change(self, form, model, is_created):
        LastUpdate().update_db()
        return super(CategoryAdminView, self).after_model_change(form, model, is_created)

    def on_model_delete(self, model):
        LastUpdate().update_db()
        return super(CategoryAdminView, self).on_model_delete(model)


class ImageAdminView(BaseModelView):
    pass


class TablesAdminView(BaseModelView):
    form_columns = ['table_id', 'chair_type', 'chair_count', 'position']
    column_list = ['table_id', 'chair_type', 'chair_count', 'position']
    column_labels = dict(table_id='№ стола', chair_type='Тип мест', chair_count='Количество мест', position='Положение стола')


class BookingAdminView(BaseModelView):
    form_columns = ['date_time_from', 'date_time_to', 'users', 'tables', 'accepted']
    column_labels = dict(date_time_from='Дата и время начала', date_time_to='Дата и время окончания',
                         users='Пользователь', tables='Стол', accepted='Подтверждено')
    column_default_sort = ('booking_id', True)
    form_args = dict(
        date_time_from=dict(label='Дата и время начала', validators=[validators.DataRequired()]),
        date_time_to=dict(label='Дата и время окончания', validators=[validators.DataRequired()]),
        users=dict(label='Пользователь', validators=[validators.DataRequired()]),
        tables=dict(label='Стол', validators=[validators.DataRequired()]),
        accepted=dict(label='Подтверждено')
    )

    def on_model_change(self, form, model, is_created):
        booking_date_time_from = request.form['date_time_from']
        booking_date_time_to = request.form['date_time_to']
        booking_table = request.form['tables']
        model_created_id = model.booking_id
        """
        if not model_created_id:
            booking = Booking.query.filter(and_(Booking.date_time_from == booking_date_time_from,
                                                Booking.date_time_to == booking_date_time_to,
                                                Booking.table_id == booking_table
                                                )).first()

            if booking:
                db.session.expunge(booking)
                raise validators.ValidationError(str(booking.booking_id))


        #booking = Booking.query.filter(and_(Booking.date_time_from == booking_date_time_from, Booking.date_time_to == booking_date_time_to, Booking.table_id == booking_table)).first()
        #validators.ValidationError(str(booking))
        #if booking:
            #raise validators.ValidationError('Запись с такими данными уже существует!')
        #else:
            #return super(BookingAdminView, self).on_model_change(form, model, is_created)
        #"""


class UsersAdminView(BaseModelView):
    form_columns = ['roles', 'email', 'name', 'surname', 'birthday', 'phone', 'active']
    column_list = ('roles', 'email', 'name', 'surname', 'birthday', 'phone', 'active')
    column_labels = dict(roles='Роль', email='Email', name='Имя', surname='Фамилия', birthday='Дата рождения',
                         phone='Телефон', active='Статус доступа')
    can_create = False
    #can_delete = False


class TimetableAdminView(BaseModelView):
    def after_model_change(self, form, model, is_created):
        TimeTableUpdate().update_db()
        return super(TimetableAdminView, self).after_model_change(form, model, is_created)

    def on_model_delete(self, model):
        TimeTableUpdate().update_db()
        return super(TimetableAdminView, self).on_model_delete(model)
