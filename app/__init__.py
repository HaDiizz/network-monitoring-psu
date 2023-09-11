from flask import Flask
import os
from dotenv import load_dotenv
from . import models
from . import acl
from . import caches
from authlib.integrations.flask_client import OAuth
from datetime import timedelta
from . import oauth2

load_dotenv()

server = Flask(__name__)
server.config['SECRET_KEY'] = os.environ['SECRET_KEY']
server.config['CACHE_TYPE'] = 'SimpleCache'
server.template_folder = 'templates'
server.config['SESSION_COOKIE_NAME'] = 'psu-passport-login-session'
server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
models.init_mongoengine(server)
acl.init_acl(server)
caches.init_cache(server)
oauth2.init_oauth(server)

from app.views import admin, site
server.register_blueprint(admin.admin_module)
server.register_blueprint(site.module)