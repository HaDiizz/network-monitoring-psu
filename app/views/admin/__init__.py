from flask import Blueprint, render_template
from ... import acl
from ...utils import address_list

admin_module = Blueprint("admin", __name__, url_prefix="/admin")

from app.views.admin.service import *
from app.views.admin.host import *
from app.views.admin.management import *

@admin_module.route("/overview")
@acl.roles_required("admin")
def index():
    return render_template("/admin/index.html", title="Overview", address_list=address_list())
