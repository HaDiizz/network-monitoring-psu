from flask_login import UserMixin
import mongoengine as me
import datetime

class User(me.Document, UserMixin):
    username = me.StringField(required=True, unique=True)
    password = me.StringField(required=True)
    email = me.StringField(required=True, unique=True)
    first_name = me.StringField(required=True)
    last_name = me.StringField(required=True)
    role = me.StringField(default="user")
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)