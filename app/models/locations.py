import mongoengine as me
import datetime


class Location(me.Document):
    location_id = me.StringField(required=True, unique=True)
    name = me.StringField(required=True, unique=True)
    lat = me.FloatField(required=True)
    lng = me.FloatField(required=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    
    def save(self, *args, **kwargs):
        self.updated_date = datetime.datetime.now
        return super(Location, self).save(*args, **kwargs)