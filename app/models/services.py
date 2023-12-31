import mongoengine as me
import datetime


class ServiceDown(me.Document):
    service_id = me.StringField(required=True)
    last_time_down = me.DateTimeField()


class ServiceList(me.Document):
    state = me.IntField(required=True)
    last_state = me.IntField(required=True)
    remark = me.StringField(default="")
    last_time_up = me.DateTimeField(required=True)
    last_time_down = me.DateTimeField()
    minutes = me.FloatField(required=True)
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    def save(self, *args, **kwargs):
        self.updated_date = datetime.datetime.now
        return super(ServiceList, self).save(*args, **kwargs)


class Service(me.Document):
    service_id = me.StringField(required=True)
    service_list = me.ListField(me.ReferenceField(ServiceList, lazy=True))
    groups = me.ListField(me.StringField())
    name = me.StringField(required=True)
    month = me.IntField(required=True)
    year = me.IntField(required=True)
    count = me.IntField(required=True)
    availability = me.FloatField(required=True)
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    def save(self, *args, **kwargs):
        self.updated_date = datetime.datetime.now
        return super(Service, self).save(*args, **kwargs)
