from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import current_user
from bson import ObjectId
from app.views.admin import admin_module
from ... import acl
from ... import models
from ... import forms
from ...helpers.utils import status_list
import mongoengine as me

@admin_module.route("/locations")
@acl.roles_required("admin")
def location():
    locations = models.Location.objects().order_by("-updated_date")
    return render_template("/admin/location/map/location.html", title="Location", locations=locations)


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
        location_id = request.form.get('location_id')
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        if name == '' or lat == '' or lng == '' or location_id == '':
            flash("กรุณาใส่ข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/location/map/createLocation.html", title="Create Location", form=form)
        existing_location = models.Location.objects.filter(me.Q(name=name) | me.Q(location_id=location_id)).first()
        if existing_location:
            flash("ชื่อสถานที่นี้มีอยู่แล้ว", "error")
            return render_template("/admin/location/map/createLocation.html", title="Create Location", form=form)
        location = models.Location(
            location_id=location_id,
            name=name,
            lat=round(float(lat), 6),
            lng=round(float(lng), 6),
        )
        location.save()
        form.location_id.data = ""
        form.name.data = ""
        form.lat.data = ""
        form.lng.data = ""
        flash("เพิ่มข้อมูลสำเร็จ", "success")
    return render_template("/admin/location/map/createLocation.html", title="Create Location", form=form)


@admin_module.route("/locations/edit/<string:location_id_prop>", methods=["GET", "POST"])
@acl.roles_required("admin")
def edit_location(location_id_prop):
    location = models.Location.objects.with_id(location_id_prop)
    if not location:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.location'))
    form = forms.LocationForm(obj=location)
    if request.method == 'POST':
        location_id = request.form.get('location_id')
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        if name == '' or lat == '' or lng == '' or location_id == '':
            flash("กรุณาใส่ข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/location/map/editLocation.html", title="Edit Location", form=form)
        existing_location = models.Location.objects.filter(me.Q(name=name) | me.Q(location_id=location_id)).first()
        if existing_location and existing_location.id != ObjectId(location_id_prop):
            flash("ชื่อสถานที่นี้มีอยู่แล้ว", "error")
            return render_template("/admin/location/map/editLocation.html", title="Edit Location", form=form)
        location.location_id = location_id
        location.name = name
        location.lat = round(float(lat), 6)
        location.lng = round(float(lng), 6)
        location.save()
        flash("แก้ไขข้อมูลสำเร็จ", "success")
    return render_template("/admin/location/map/editLocation.html", title="Edit Location", form=form)


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
        return redirect("/admin/overview/access-point")


@admin_module.route("/reports", methods=["GET", "POST"])
@acl.roles_required("admin")
def report():
    form = forms.ReportFilterForm()
    reports = models.Report.objects()
    total_reports = reports.filter().count()
    pending_reports = reports.filter(status='PENDING').count()
    completed_reports = reports.filter(status='COMPLETED').count()
    checking_reports = reports.filter(status='CHECKING').count()
    rejected_reports = reports.filter(status='REJECTED').count()
    status_counts = {
        'TOTAL': total_reports,
        'PENDING': pending_reports,
        'COMPLETED': completed_reports,
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
    categories = models.Category.objects()
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        category_id = request.form.get('category_id')
        if not category_id or category_id == "":
            flash("เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง", "error")
            return render_template("/admin/issueCategory.html", title="Issue Category", categories=categories)
        if not category_name or category_name == "":
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/issueCategory.html", title="Issue Category", categories=categories)
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


@admin_module.route("/service-level-agreement", methods=["GET", "POST"])
@acl.roles_required("admin")
def sla_configuration():
    sla_configs = models.SLAConfig.objects()
    if request.method == 'POST':
        category = request.form.get('category')
        year = request.form.get('year')
        ok_status = float(request.form.get('ok_status'))
        critical_status = float(request.form.get('critical_status'))
        if year is None or year == '' or ok_status is None or ok_status == '' or critical_status is None or critical_status == '' or category is None or category == '':
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)
        if category not in ("Host", "Service", "All"):
            flash("ข้อมูลไม่ถูกต้อง", "error")
            return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)
        duplicate_year = models.SLAConfig.objects(year=year, category=category)
        if duplicate_year:
            flash(f"พบข้อมูลซ้ำซ้อน {category} - {year}", "error")
            return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)
        if ok_status <= critical_status:
            flash("State conflict", "error")
            return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)
        if category == "All":
            sla_config_host = models.SLAConfig(
                category="Host",
                year=year,
                ok_status=ok_status,
                critical_status=critical_status,
            )
            sla_config_host.save()
            sla_config_service = models.SLAConfig(
                category="Service",
                year=year,
                ok_status=ok_status,
                critical_status=critical_status,
            )
            sla_config_service.save()
            sla_config_accessPoint = models.SLAConfig(
                category="Access Point",
                year=year,
                ok_status=ok_status,
                critical_status=critical_status,
            )
            sla_config_accessPoint.save()
        else:
            sla_config = models.SLAConfig(
                category=category,
                year=year,
                ok_status=ok_status,
                critical_status=critical_status,
            )
            sla_config.save()  
        flash("เพิ่มข้อมูลสำเร็จ", "success")
    return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)


@admin_module.route("/service-level-agreement/edit", methods=["POST", "GET"])
@acl.roles_required("admin")
def edit_sla_configuration():
    sla_configs = models.SLAConfig.objects()
    if request.method == 'POST':
        category = request.form.get('category')
        year = request.form.get('year')
        ok_status = float(request.form.get('ok_status'))
        critical_status = float(request.form.get('critical_status'))
        sla_config_id = request.form.get('sla_config_id')
        if not sla_config_id or sla_config_id == "":
            flash("เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง", "error")
            return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)
        if year is None or year == '' or ok_status is None or ok_status == '' or critical_status is None or critical_status == '':
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/slaConfiguration.html", title="Issue Category", sla_configs=sla_configs)
        duplicate_doc = models.SLAConfig.objects.with_id(sla_config_id)
        if duplicate_doc.category != category:
                flash("ไม่สามารถเปลี่ยน Category ได้", "error")
                return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)
        duplicate_year = models.SLAConfig.objects(year=int(year), category=category).first()
        if duplicate_year:
            if duplicate_year.id != ObjectId(sla_config_id):
                flash(f"พบข้อมูลซ้ำซ้อน {category} - {year}", "error")
                return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)
        if ok_status <= critical_status:
            flash("State conflict", "error")
            return render_template("/admin/slaConfiguration.html", title="SLA Requirements", sla_configs=sla_configs)
        sla_config = models.SLAConfig.objects.with_id(sla_config_id)
        sla_config.year = int(year)
        sla_config.ok_status = float(ok_status)
        sla_config.critical_status = float(critical_status)
        sla_config.save()
        flash("แก้ไขข้อมูลสำเร็จ", "success")
    return redirect(url_for('admin.sla_configuration'))

@admin_module.route("/service-level-agreement/delete/<string:sla_config_id>")
@acl.roles_required("admin")
def delete_sla_config(sla_config_id):
    sla_config = models.SLAConfig.objects.with_id(sla_config_id)
    if not sla_config:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.sla_configuration'))
    sla_config.delete()
    flash('ลบข้อมูลสำเร็จ', 'success')
    return redirect(url_for('admin.sla_configuration'))


@admin_module.route("/access-point-location")
@acl.roles_required("admin")
def access_point_location():
    accessPoints = models.AccessPointLocation.objects().order_by("-updated_date")
    return render_template("/admin/location/access-point/accessPointLocation.html", title="Access Point Location", accessPoints=accessPoints)


@admin_module.route("/access-point-location/create",  methods=["GET", "POST"])
@acl.roles_required("admin")
def create_access_point_location():
    if request.method == 'POST':
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        floor = request.form.get('floor')
        room = request.form.get('room')
        if name == '' or lat == '' or lng == '':
            flash("กรุณาใส่ข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/location/access-point/create.html", title="Create Access Point Location")
        existing_name = models.AccessPointLocation.objects.filter(me.Q(name=name)).first()
        if existing_name:
            flash("ชื่อแอคเซสพอยต์ซ้ำ", "error")
            return render_template("/admin/location/access-point/create.html", title="Create Access Point Location")
        accessPoint = models.AccessPointLocation(
            name=name,
            coordinates=(round(float(lat), 6), round(float(lng), 6)),
            floor=floor,
            room=room
        )
        accessPoint.save()
        flash("เพิ่มข้อมูลสำเร็จ", "success")
    return render_template("/admin/location/access-point/create.html", title="Create Access Point Location")


@admin_module.route("/access-point-location/edit/<string:access_point_id>", methods=["GET", "POST"])
@acl.roles_required("admin")
def edit_access_point_location(access_point_id):
    accessPoint = models.AccessPointLocation.objects.with_id(access_point_id)
    if not accessPoint:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.access_point_location'))
    if request.method == 'POST':
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        floor = request.form.get('floor')
        room = request.form.get('room')
        if name == '' or lat == '' or lng == '':
            flash("กรุณาใส่ข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/location/access-point/edit.html", title="Edit Access Point Location", accessPoint=accessPoint)
        existing_name = models.AccessPointLocation.objects.filter(me.Q(name=name)).first()
        if existing_name and existing_name.id != ObjectId(access_point_id):
            flash("ชื่อแอคเซสพอยต์ซ้ำ", "error")
            return render_template("/admin/location/access-point/edit.html", title="Edit Access Point Location", accessPoint=accessPoint)
        accessPoint.name = name
        accessPoint.floor = floor
        accessPoint.room = room
        accessPoint.coordinates = (round(float(lat), 6), round(float(lng), 6))
        accessPoint.save()
        flash("แก้ไขข้อมูลสำเร็จ", "success")
    return render_template("/admin/location/access-point/edit.html", title="Edit Access Point Location", accessPoint=accessPoint)


@admin_module.route("/access-point-location/delete/<string:access_point_id>")
@acl.roles_required("admin")
def delete_access_point_location(access_point_id):
    accessPoint = models.AccessPointLocation.objects.with_id(access_point_id)
    if not accessPoint:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.access_point_location'))
    accessPoint.delete()
    flash('ลบข้อมูลสำเร็จ', 'success')
    return redirect(url_for('admin.access_point_location'))


@admin_module.route("/host-location")
@acl.roles_required("admin")
def host_location():
    hosts = models.HostLocation.objects().order_by("-updated_date")
    return render_template("/admin/location/host/hostLocation.html", title="Host Location", hosts=hosts)


@admin_module.route("/host-location/create",  methods=["GET", "POST"])
@acl.roles_required("admin")
def create_host_location():
    if request.method == 'POST':
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        floor = request.form.get('floor')
        room = request.form.get('room')
        if name == '' or lat == '' or lng == '':
            flash("กรุณาใส่ข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/location/host/create.html", title="Create Host Location")
        existing_name = models.HostLocation.objects.filter(me.Q(name=name)).first()
        if existing_name:
            flash("ชื่อโฮสต์ซ้ำ", "error")
            return render_template("/admin/location/host/create.html", title="Create Host Location")
        host = models.HostLocation(
            name=name,
            coordinates=(round(float(lat), 6), round(float(lng), 6)),
            floor=floor,
            room=room
        )
        host.save()
        flash("เพิ่มข้อมูลสำเร็จ", "success")
    return render_template("/admin/location/host/create.html", title="Create Host Location")


@admin_module.route("/host-location/edit/<string:host_id>", methods=["GET", "POST"])
@acl.roles_required("admin")
def edit_host_location(host_id):
    host = models.HostLocation.objects.with_id(host_id)
    if not host:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.host_location'))
    if request.method == 'POST':
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        floor = request.form.get('floor')
        room = request.form.get('room')
        if name == '' or lat == '' or lng == '':
            flash("กรุณาใส่ข้อมูลให้ครบถ้วน", "error")
            return render_template("/admin/location/host/edit.html", title="Edit Host Location", host=host)
        existing_name = models.HostLocation.objects.filter(me.Q(name=name)).first()
        if existing_name and existing_name.id != ObjectId(host_id):
            flash("ชื่อโฮสต์ซ้ำ", "error")
            return render_template("/admin/location/host/edit.html", title="Edit Host Location", host=host)
        host.name = name
        host.floor = floor
        host.room = room
        host.coordinates = (round(float(lat), 6), round(float(lng), 6))
        host.save()
        flash("แก้ไขข้อมูลสำเร็จ", "success")
    return render_template("/admin/location/host/edit.html", title="Edit Host Location", host=host)


@admin_module.route("/host-location/delete/<string:host_id>")
@acl.roles_required("admin")
def delete_host_location(host_id):
    host = models.HostLocation.objects.with_id(host_id)
    if not host:
        flash('ไม่พบข้อมูลที่ต้องการ', 'error')
        return redirect(url_for('admin.host_location'))
    host.delete()
    flash('ลบข้อมูลสำเร็จ', 'success')
    return redirect(url_for('admin.host_location'))
