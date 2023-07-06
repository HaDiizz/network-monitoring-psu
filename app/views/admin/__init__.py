from flask import Blueprint

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

from app.views.admin.dashboard import *
from app.views.admin.management import *
from app.views.admin.setting import *

@admin_blueprint.route("/")
def index():
    return "admin index"
