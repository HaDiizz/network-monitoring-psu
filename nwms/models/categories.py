import mongoengine as me
import datetime

class Category(me.Document):
    category_name = me.StringField(required=True, max_length=100)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now, auto_now=True)
    
    def save(self, *args, **kwargs):
        self.updated_date = datetime.datetime.now
        return super(Category, self).save(*args, **kwargs)