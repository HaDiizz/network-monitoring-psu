from flask import render_template
from app.views.admin import admin_module
from ... import acl
from ...dash.service_monthly import dash_service
import calendar
from ...helpers.utils import get_day_data, get_quarter_data, sla_status_list
from ... import models

@admin_module.route("/services")
@acl.roles_required("admin")
def service():
    return render_template("/admin/service/index.html", title="Service", dash_service=dash_service.index())

@admin_module.route("/services/<int:year>/<string:month>")
@acl.roles_required("admin")
def service_quarterly(year, month):
    return render_template("/admin/service/quarterly.html", title="Service Quarterly")