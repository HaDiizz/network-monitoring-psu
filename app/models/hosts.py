import mongoengine as me
import datetime


class HostList(me.Document):
    state = me.IntField(required=True)
    last_state = me.IntField(required=True)
    notified = me.BooleanField(required=True)
    remark = me.StringField(default="")
    last_time_up = me.DateTimeField(required=True)
    last_time_down = me.DateTimeField()
    minutes = me.IntField(required=True)
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    def save(self, *args, **kwargs):
        self.updated_date = datetime.datetime.now
        return super(HostList, self).save(*args, **kwargs)


class Host(me.Document):
    host_id = me.StringField(required=True)
    host_list = me.ListField(me.ReferenceField(HostList, lazy=True))
    name = me.StringField(required=True)
    ip_address = me.StringField(required=True)
    month = me.IntField(required=True)
    year = me.IntField(required=True)
    count = me.IntField(required=True)
    availability = me.FloatField(required=True)
    coordinates = me.GeoPointField(required=True)
    floor = me.StringField(required=True)
    room = me.StringField(required=True)
    created_date = me.DateTimeField(
        required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    def save(self, *args, **kwargs):
        self.updated_date = datetime.datetime.now
        return super(Host, self).save(*args, **kwargs)
