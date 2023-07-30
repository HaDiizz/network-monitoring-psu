import mongoengine as me
import datetime


class Address(me.Document):
    name = me.StringField(required=True, unique=True)
    lat = me.FloatField(required=True)
    lng = me.FloatField(required=True)
