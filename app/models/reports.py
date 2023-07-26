import mongoengine as me
import datetime
from .users import User

class Report(me.Document):
    reported_by = me.ReferenceField(User, required=True)
    title = me.StringField(required=True, max_length=100)
    detail = me.StringField(required=True, max_length=300)
    lat = me.FloatField(required=True)
    lng = me.FloatField(required=True)
    status = me.StringField(required=True, default="PENDING")
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)