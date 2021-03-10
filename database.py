# database.py
import mongoengine as me
from flask_mongoengine import MongoEngine 
from flask_mongoengine.wtf import model_form

eng = MongoEngine()

class User(me.Document):
    username     = me.StringField(required=True, unique=True)
    firstname    = me.StringField(required=True)
    lastname     = me.StringField(required=True)
    email        = me.StringField(required=True)
    passwordhash = me.StringField(required=True)
    roles        = me.ListField(me.StringField(), 
                    required=False, default=[])
