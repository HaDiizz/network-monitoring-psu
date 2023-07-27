from flask import render_template, redirect, request, url_for, flash
from app.views.admin import admin_module
from ... import acl
from ... import models
from ... import forms
from ...utils import status_list

@admin_module.route("/permission")
@acl.roles_required("admin")
def permission():
    return render_template("/admin/permission.html", title="Permission")

@admin_module.route("/reports", methods=["GET", "POST"])
@acl.roles_required("admin")
def report():
    form = forms.report.ReportFilterForm()
    reports = models.Report.objects()
    total_reports = reports.filter().count()
    pending_reports = reports.filter(status='PENDING').count()
    approved_reports = reports.filter(status='APPROVED').count()
    checking_reports = reports.filter(status='CHECKING').count()
    rejected_reports = reports.filter(status='REJECTED').count()
    status_counts = {
        'TOTAL': total_reports,
        'PENDING': pending_reports,
        'APPROVED': approved_reports,
        'CHECKING': checking_reports,
        'REJECTED': rejected_reports,
    }
    if form.validate_on_submit():
        status = form.status.data
        query_filter = {}
        if status and status != 'ALL':
            query_filter['status'] = status

        reports = reports.filter(**query_filter)
    return render_template("/admin/report.html", title="Report", reports=reports, form=form, status_counts=status_counts)

@admin_module.route("/reports/<string:report_id>", methods=["GET", "POST"])
@acl.roles_required("admin")
def reportDetail(report_id):
    try:
        report = models.Report.objects.with_id(report_id).select_related()
        if request.method == 'POST':
            new_status = request.form.get('status')
            report.status = new_status
            report.save()
            flash("เปลี่ยนสถานะเป็น '{new_status}' สำเร็จ".format(new_status=new_status), "success")
            return redirect(url_for("admin.reportDetail", report_id=report_id))
        return render_template("/admin/reportDetail.html", title="Report Detail", report=report, status_list=status_list())
    except Exception as e:
        flash("ขออภัย มีข้อผิดพลาดเกิดขึ้น", "error")
        return redirect("/admin/reports")