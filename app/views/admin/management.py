from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import current_user
from bson import ObjectId
from app.views.admin import admin_module
from ... import acl
from ... import models
from ... import forms
from ...utils import status_list


@admin_module.route("/locations")
@acl.roles_required("admin")
def location():
    locations = models.Location.objects().order_by("-updated_date")
    return render_template("/admin/location.html", title="Location", locations=locations)


@admin_module.route("/locations/delete/<string:location_id>")
@acl.roles_required("admin")
def delete_location(location_id):
    location = models.Location.objects.with_id(location_id)
    if not location:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.location'))
    location.delete()
    flash('ลบข้อมูลสำเร็จ', 'success')
    return redirect(url_for('admin.location'))


@admin_module.route("/locations/create", methods=["GET", "POST"])
@acl.roles_required("admin")
def create_location():
    form = forms.LocationForm()
    if request.method == 'POST':
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        if name == '' or lat == '' or lng == '':
            flash("กรุณาใส่ข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/createLocation.html", title="Create Location", form=form)
        existing_location = models.Location.objects(name=name).first()
        if existing_location:
            flash("ชื่อสถานที่นี้มีอยู่แล้ว", "error")
            return render_template("/admin/createLocation.html", title="Create Location", form=form)
        location = models.Location(
            name=name,
            lat=round(float(lat), 6),
            lng=round(float(lng), 6),
        )
        location.save()
        form.name.data = ""
        flash("เพิ่มข้อมูลสำเร็จ", "success")
    return render_template("/admin/createLocation.html", title="Create Location", form=form)


@admin_module.route("/locations/edit/<string:location_id>", methods=["GET", "POST"])
@acl.roles_required("admin")
def edit_location(location_id):
    location = models.Location.objects.with_id(location_id)
    if not location:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.location'))
    form = forms.LocationForm(obj=location)
    if request.method == 'POST':
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        if name == '' or lat == '' or lng == '':
            flash("กรุณาใส่ข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/editLocation.html", title="Edit Location", form=form)
        existing_location = models.Location.objects(name=name).first()
        if existing_location and existing_location.id != ObjectId(location_id):
            flash("ชื่อสถานที่นี้มีอยู่แล้ว", "error")
            return render_template("/admin/editLocation.html", title="Edit Location", form=form)
        location.name = name
        location.lat = round(float(lat), 6)
        location.lng = round(float(lng), 6)
        location.save()
        flash("แก้ไขข้อมูลสำเร็จ", "success")
    return render_template("/admin/editLocation.html", title="Edit Location", form=form)


@admin_module.route("/permission", methods=["GET", "POST"])
@acl.roles_required("admin")
def permission():
    try:
        users = models.User.objects()
        if request.method == 'POST':
            user_id = ObjectId(request.form.get('user_id'))
            is_admin = request.form.get('is_admin')
            if user_id == current_user.id:
                abort(403)
            new_role = 'admin' if is_admin == "true" else 'user'
            user = models.User.objects.with_id(user_id)
            user.role = new_role
            user.save()
        return render_template("/admin/permission.html", title="Permission", users=users)
    except Exception as e:
        flash("ขออภัย มีข้อผิดพลาดเกิดขึ้น", "error")
        return redirect("/admin/overview")


@admin_module.route("/reports", methods=["GET", "POST"])
@acl.roles_required("admin")
def report():
    form = forms.ReportFilterForm()
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
            flash("เปลี่ยนสถานะเป็น '{new_status}' สำเร็จ".format(
                new_status=new_status), "success")
            return redirect(url_for("admin.reportDetail", report_id=report_id))
        return render_template("/admin/reportDetail.html", title="Report Detail", report=report, status_list=status_list())
    except Exception as e:
        flash("ขออภัย มีข้อผิดพลาดเกิดขึ้น", "error")
        return redirect("/admin/reports")


@admin_module.route("/categories", methods=["GET", "POST"])
@acl.roles_required("admin")
def category():
    categories = models.Category.objects()
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        if not category_name or category_name == "":
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/issueCategory.html", title="Issue Category")
        category = models.Category(
            category_name=category_name
        )
        category.save()
        flash("เพิ่มข้อมูลสำเร็จ", "success")
    return render_template("/admin/issueCategory.html", title="Issue Category", categories=categories)


@admin_module.route("/categories/edit", methods=["POST"])
@acl.roles_required("admin")
def edit_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        category_id = request.form.get('category_id')
        if not category_id or category_id == "":
            flash("เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง", "error")
            return render_template("/admin/issueCategory.html", title="Issue Category")
        if not category_name or category_name == "":
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/issueCategory.html", title="Issue Category")
        category = models.Category.objects.with_id(category_id)
        category.category_name = category_name
        category.save()
        flash("แก้ไขข้อมูลสำเร็จ", "success")
    return redirect(url_for('admin.category'))


@admin_module.route("/categories/delete/<string:category_id>")
@acl.roles_required("admin")
def delete_category(category_id):
    category = models.Category.objects.with_id(category_id)
    if not category:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.category'))
    category.delete()
    flash('ลบข้อมูลสำเร็จ', 'success')
    return redirect(url_for('admin.category'))
