from flask import render_template
from app.views.admin import admin_module
from ... import acl

@admin_module.route("/hosts")
@acl.roles_required("admin")
def host():
    return render_template("/admin/host/index.html", title="Host")

@admin_module.route("/hosts/<int:year>/<string:month>")
@acl.roles_required("admin")
def host_quarterly(year, month):
    return render_template("/admin/host/quarterly.html", title="Host Quarterly")