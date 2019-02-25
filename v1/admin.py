from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import form
from wtforms import FileField
from models import *


# Create class our AdminView
class BaseModelView(ModelView):
    def on_model_change(self, form, model, is_created):
        # Call function, which refreshes db-update date
        image = LastUpdate().update_db()

    def on_model_delete(self, model):
        image = LastUpdate().update_db()


# Create class MenuAdminView for Menu
class MenuAdminView(BaseModelView):
    # Add extra field for uploading image
    form_extra_fields = {
        'file': FileField('File')
    }
    # Add necessary fields ( because we need to hide 'photo' field
    form_columns = ['Class', 'name', 'price', 'desc_short', 'desc_long', 'weight', 'recommended', 'file']
    """
    # Load image in DB when model changes
    def on_model_change(self, form, model, is_created):
        # Call function, which refreshes db-update date
        model.load_image()
        return super(MenuAdminView, self).on_model_change(form, model, is_created)
    """

    def after_model_change(self, form, model, is_created):
        model.load_image()
        return super(MenuAdminView, self).on_model_change(form, model, is_created)

    # Delete all images, connected with current model
    def on_model_delete(self, model):
        model.delete_image()
        return super(MenuAdminView, self).on_model_delete(model)


class ClassAdminView(BaseModelView):
    pass


class ImageAdminView(BaseModelView):
    pass

