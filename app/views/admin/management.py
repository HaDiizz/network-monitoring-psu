from flask import render_template
from app.views.admin import admin_module
from ... import acl

@admin_module.route("/permission")
@acl.roles_required("admin")
def permission():
    return render_template("/admin/permission.html", title="Permission")

@admin_module.route("/reports")
@acl.roles_required("admin")
def report():
    return render_template("/admin/report.html", title="Report")

@admin_module.route("/reports/<string:id>")
@acl.roles_required("admin")
def reportDetail(id):
    return render_template("/admin/reportDetail.html", title="Report Detail")