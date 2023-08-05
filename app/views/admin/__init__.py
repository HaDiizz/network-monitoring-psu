from flask import Blueprint, render_template
from ... import acl
from ...utils import location_list, host_list

admin_module = Blueprint("admin", __name__, url_prefix="/admin")

from app.views.admin.service import *
from app.views.admin.host import *
from app.views.admin.management import *

@admin_module.route("/overview")
@acl.roles_required("admin")
def index():
    hosts = host_list()
    if not hosts:
        hosts = []
    return render_template("/admin/index.html", title="Overview", location_list=location_list(), host_list=hosts)
