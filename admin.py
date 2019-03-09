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
    # When change any model in admin panel
    def on_model_change(self, form, model, is_created):
        # Call function, which refreshes db-update date
        image = LastUpdate().update_db()

    # When delete ange any model in admin panel
    def on_model_delete(self, model):
        # Call function, which refreshes db-update date
        image = LastUpdate().update_db()


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
    form_columns = ['photo','Category', 'name', 'price', 'desc_short', 'desc_long', 'weight',
                    'recommended', 'file', 'delivery']


    # Upload image to DB after model changed
    def after_model_change(self, form, model, is_created):
        model.load_image()
        return super(MenuAdminView, self).on_model_change(form, model, is_created)

    # Delete all images, connected with current model
    def on_model_delete(self, model):
        model.delete_image()
        return super(MenuAdminView, self).on_model_delete(model)


class CategoryAdminView(BaseModelView):
    pass


class ImageAdminView(BaseModelView):
    pass


class TablesAdminView(BaseModelView):
    pass

class BookingAdminView(BaseModelView):
    pass



class UsersAdminView(BaseModelView):
    form_columns = ['roles', 'email', 'name', 'surname', 'birthday', 'phone', 'active']
    column_list = ('roles', 'email', 'name', 'surname', 'birthday', 'phone', 'active')
    can_create = False
    can_delete = False
