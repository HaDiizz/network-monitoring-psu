import os
import mongoengine as me

from .users import User
from .locations import Location
from .reports import Report
from .categories import Category
from .hosts import Host
from .hosts import HostList
from .hosts import HostDown
from .oauth2 import OAuth2Token
from .sla_config import SLAConfig
from .services import Service
from .services import ServiceList
from .services import ServiceDown
from .accesspoints import AccessPoint
from .accesspoints import AccessPointList
from .accesspoints import AccessPointDown
from .accesspoints import AccessPointLocation

def init_mongoengine(server):
    server.config['MONGODB_SETTINGS'] = {
    'db': os.environ['MONGODB_NAME'],
    'host': os.environ['MONGODB_HOST']
    }
    try:
        me.connect(os.environ['MONGODB_NAME'], host=os.environ['MONGODB_HOST'], alias='default')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print("Failed to connect to MongoDB:", str(e))