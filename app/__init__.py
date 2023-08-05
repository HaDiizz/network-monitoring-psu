from app.views import admin, site
from flask import Flask
import os
from dotenv import load_dotenv
from . import models
from . import acl
from . import caches

load_dotenv()

server = Flask(__name__)
server.config['SECRET_KEY'] = os.environ['SECRET_KEY']
server.config['CACHE_TYPE'] = 'SimpleCache'
server.template_folder = 'templates'
models.init_mongoengine(server)
acl.init_acl(server)
caches.init_cache(server)

server.register_blueprint(admin.admin_module)
server.register_blueprint(site.module)