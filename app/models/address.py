import mongoengine as me
import datetime

class Address(me.Document):
    name = me.StringField(required=True, unique=True)
    lat = me.FloatField(required=True)
    lng = me.FloatField(required=True)
    floor = me.StringField()
    room = me.StringField()
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)