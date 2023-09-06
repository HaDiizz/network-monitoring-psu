import os
import mongoengine as me

from .users import User
from .locations import Location
from .reports import Report
from .categories import Category
from .hosts import Host
from .hosts import HostList
# from .services import Service

def init_mongoengine(server):
    server.config['MONGODB_SETTINGS'] = {
    'db': os.environ['MONGODB_NAME'],
    'host': os.environ['MONGODB_HOST']
    }
    try:
        me.connect(os.environ['MONGODB_NAME'], host=os.environ['MONGODB_HOST'])
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print("Failed to connect to MongoDB:", str(e))