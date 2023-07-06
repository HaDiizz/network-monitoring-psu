from app.views import admin, site
from flask import Flask

server = Flask(__name__)

server.register_blueprint(admin.admin_blueprint)
server.register_blueprint(site.site_blueprint)