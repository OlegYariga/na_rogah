from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask import redirect, url_for
from flask_admin import AdminIndexView
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
        'file': FileField('File')
    }
    # Add necessary fields ( because we need to hide 'photo' field
    form_columns = ['Category', 'name', 'price', 'desc_short', 'desc_long', 'weight',
                    'recommended', 'file', 'delivery']

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
    pass


class BookingAdminView(BaseModelView):
    form_columns = ['date_time_from', 'date_time_to', 'users', 'tables', 'accepted']
    pass


class UsersAdminView(BaseModelView):
    form_columns = ['roles', 'email', 'name', 'surname', 'birthday', 'phone', 'active']
    column_list = ('roles', 'email', 'name', 'surname', 'birthday', 'phone', 'active')
    can_create = False
    #can_delete = False


class TimetableAdminView(BaseModelView):
    def after_model_change(self, form, model, is_created):
        TimeTableUpdate().update_db()
        return super(TimetableAdminView, self).after_model_change(form, model, is_created)

    def on_model_delete(self, model):
        TimeTableUpdate().update_db()
        return super(TimetableAdminView, self).on_model_delete(model)
