from flask import render_template
from nwms.web.views.admin import admin_module
from nwms.web import acl

@admin_module.route("/services")
@acl.roles_required("admin")
def service():
    return render_template("/admin/service/index.html", title="Service")

@admin_module.route("/services/<int:year>/<string:month>")
@acl.roles_required("admin")
def service_quarterly(year, month):
    return render_template("/admin/service/quarterly.html", title="Service Quarterly")