import mongoengine as me
import datetime

class SLAConfig(me.Document):
    category = me.StringField(required=True)
    year = me.IntField(required=True)
    ok_status = me.FloatField(required=True)
    critical_status = me.FloatField(required=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)
    
    def save(self, *args, **kwargs):
        self.updated_date = datetime.datetime.now
        return super(SLAConfig, self).save(*args, **kwargs)