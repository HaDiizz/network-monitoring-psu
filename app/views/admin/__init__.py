from flask import Blueprint, render_template, jsonify
from ... import acl
from ...helpers.api import host_list, host_group_list, service_group_list, maintain_host_list, maintain_service_list, access_point_list, get_all_service_list, access_point_list, host_list_info, ap_in_downtime
from ...helpers.utils import location_list, get_host_down_select_time, get_ap_list_with_sla, get_ap_name_list, get_host_name_list, get_all_host_list, get_accessPoint_down_select_time
from app import caches
import datetime

admin_module = Blueprint("admin", __name__, url_prefix="/admin")

from app.views.admin.service import *
from app.views.admin.host import *
from app.views.admin.management import *


@admin_module.route("/overview/access-point")
@acl.roles_required("admin")
def access_point_dashboard():
    accessPoints_resp = access_point_list()
    maintain_access_points = ap_in_downtime()
    if accessPoints_resp is None:
        accessPoints_resp = []
    accessPoints = get_ap_list_with_sla(accessPoints_resp)

    accessPoint_summary = {}
    if accessPoints:
        for accessPoint in accessPoints:
            accessPoint_last_state = accessPoint["state"]
            if accessPoint_last_state == 0:
                accessPoint_state = "OK" 
            elif accessPoint_last_state == 1:
                accessPoint_state = "WARN"
            elif accessPoint_last_state == 2:
                accessPoint_state = "CRIT"
            elif accessPoint_last_state == 3:
                accessPoint_state = "UNKNOWN" 
            for maintain_access_point in maintain_access_points:
                if accessPoint["accessPoint_id"] == maintain_access_point["id"]:
                    accessPoint_state = "MAINTAIN"
                    accessPoint["state"] = -1
            if accessPoint_state not in accessPoint_summary:
                accessPoint_summary[accessPoint_state] = 0
            accessPoint_summary[accessPoint_state] += 1
        accessPoint_summary["TOTAL"] = len(accessPoints)
    return render_template("/admin/overview/accessPoint.html", title="AccessPoint", location_list=location_list(), accessPoint_summary=accessPoint_summary, access_point_list=accessPoints)


@admin_module.route("/overview/host")
@acl.roles_required("admin")
def host_dashboard():
    get_host_data = host_list_info()
    hosts = get_all_host_list(get_host_data)
    host_groups = host_group_list()
    maintain_hosts = maintain_host_list()
    now = datetime.datetime.now()
    month = calendar.month_name[now.month]
    year = now.year

    if not host_groups:
        host_groups = []
    if not hosts:
        hosts = []
    host_summary = {}
    if hosts:
        for host in hosts:
            host_state = host["state"]
            if host_state == 0:
                host_state = "UP"
            elif host_state == 1:
                host_state = "DOWN"
            elif host_state == 2:
                host_state = "UNREACH"
            for maintain_host in maintain_hosts:
                if host["host_id"] == maintain_host["id"]:
                    host_state = "MAINTAIN"
                    host["state"] = -1
            if host_state not in host_summary:
                host_summary[host_state] = 0
            host_summary[host_state] += 1
        host_summary["TOTAL"] = len(hosts)
    return render_template("/admin/overview/host.html", title="Host", location_list=location_list(), host_list=hosts, host_summary=host_summary, host_group_list=host_groups, month=month, year=year)


@admin_module.route("/overview/service")
@acl.roles_required("admin")
@caches.cache.cached(timeout=3600, key_prefix='service_dashboard')
def service_dashboard():
    services = get_all_service_list()
    service_groups = service_group_list(True)
    maintain_services = maintain_service_list()
    now = datetime.datetime.now()
    month = calendar.month_name[now.month]
    year = now.year
    
    if not service_groups:
        service_groups = []
    if not services:
        services = []
    service_summary = {}
    if services:
        for service in services:
            service_state = service["extensions"]["state"]
            if service_state == 0:
                service_state = "OK" 
            elif service_state == 1:
                service_state = "WARN"
            elif service_state == 2:
                service_state = "CRIT"
            elif service_state == 3:
                service_state = "UNKNOWN" 
            for maintain_service in maintain_services:
                if service["id"] == maintain_service["id"]:
                    service_state = "MAINTAIN"
                    service["extensions"]["state"] = -1
            if service_state not in service_summary:
                service_summary[service_state] = 0
            service_summary[service_state] += 1
        service_summary["TOTAL"] = len(services)
    return render_template("/admin/overview/service.html", title="Service", service_list=services, service_summary=service_summary, service_group_list=service_groups, month=month, year=year)


@admin_module.route("/get-latest-access-point", methods=["POST", "GET"])
@acl.roles_required("admin")
def get_latest_access_point():
    get_ap_data = access_point_list()
    result = get_ap_name_list(get_ap_data)
    existing_entries = models.AccessPointLocation.objects(name__in=[item['name'] for item in result])
    new_entries = [item for item in result if item['name'] not in [entry.name for entry in existing_entries]]
    for entry in new_entries:
        ap = models.AccessPointLocation(name=entry['name'])
        ap.save()
    return jsonify(new_entries)


@admin_module.route('/get-host-locations')
@acl.roles_required("admin")
def get_host_locations():
    location_data = []
    host_data = models.HostLocation.objects()
    for item in host_data:
        location_data.append({
            "name": item.name,
            "lat": item.coordinates[0],
            "lng": item.coordinates[1],
            "floor": item.floor,
            "room": item.room
        })
    return jsonify(location_data)


@acl.roles_required("admin")
@admin_module.route('/get-hosts')
def get_hosts():
    get_host_data = host_list_info()
    result = get_all_host_list(get_host_data)

    return jsonify(result)


@admin_module.route('/get-host/<string:host_id>')
@acl.roles_required("admin")
def get_host(host_id):
    try:
        times_list = []
        status_list = []
        data_filter = []
        host_list_ids = []
        now = datetime.datetime.now()
        selected_month = now.month
        selected_year = now.year
        selected_date = now.day
        host = models.Host.objects(
            host_id=host_id, month=selected_month, year=selected_year).first()
        if host:
            for host in host.host_list:
                host_list_ids.append(host["id"])
            query = models.HostList.objects(id__in=host_list_ids)
            query_host_list = query.all()

            for hour in range(24):
                for minute in range(0, 60, 10):
                    time_str = f"{hour:02d}:{minute:02d}"
                    times_list.append(time_str)

            for item in query_host_list:
                created_date = item["created_date"]
                day = created_date.day
                month = created_date.month
                year = created_date.year
                if day == selected_date and month == selected_month and year == selected_year:
                    data_filter.append(item)

            for i in times_list:
                status_list.append(1)

            for item in data_filter:
                last_state = item["last_state"]
                time_add = item["created_date"]
                if last_state != -1 :
                    time_hour = time_add.hour
                    time_minutes = time_add.minute
                    time_hour = time_hour * 6
                    time_minutes = int(time_minutes / 10)
                    time_down = int(item["minutes"] / 10)

                    start_time = time_hour + time_minutes
                    end_time = start_time + time_down

                else :
                    time_hour = time_add.hour
                    time_minutes = time_add.minute
                    time_hour = time_hour * 6
                    time_minutes = int(time_minutes / 10)
                    start_time = time_hour + time_minutes

                    my_datetime = datetime.datetime.now()
                    hour = int(my_datetime.strftime("%H"))
                    minute = int(my_datetime.strftime("%M"))
                    hour = hour * 6
                    minute = int(minute / 10)
                    end_time = hour + minute

                for i in range(start_time, end_time + 1):
                    status_list[i] = 0
                    

            if data_filter:
                my_datetime = datetime.datetime.now()
                hour = int(my_datetime.strftime("%H"))
                minute = int(my_datetime.strftime("%M"))
                hour = hour * 6
                minute = int(minute / 10)
                start_time = hour + minute
                end_time = len(status_list)
                
                for i in range(start_time, end_time):
                    status_list[i] = ""

            if not data_filter:
                if len(query_host_list) != 0:

                    last_state = query_host_list[len(
                        query_host_list)-1]["last_state"]
                    if last_state == -1:
                        for i in range(0, 144):
                            status_list[i] = 0
                            
            
            if not data_filter:
                my_datetime = datetime.datetime.now()
                hour = int(my_datetime.strftime("%H"))
                minute = int(my_datetime.strftime("%M"))
                hour = hour * 6
                minute = int(minute / 10)
                start_time = hour + minute
                end_time = len(status_list)

                for i in range(start_time, end_time):
                    status_list[i] = ""

            
            x_values = times_list
            y_values = status_list

            return jsonify(x_values, y_values)
        else:
            return jsonify({"error": "Host not found"}), 404
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@admin_module.route("/get-latest-host", methods=["POST", "GET"])
@acl.roles_required("admin")
def get_latest_host():
    get_hosts = host_list()
    result = get_host_name_list(get_hosts)
    existing_entries = models.HostLocation.objects(name__in=[item['name'] for item in result])
    new_entries = [item for item in result if item['name'] not in [entry.name for entry in existing_entries]]
    for entry in new_entries:
        host = models.HostLocation(name=entry['name'])
        host.save()
    return jsonify(new_entries)


@admin_module.route("/down-hosts", methods=["GET", "POST"])
@acl.roles_required("admin")
def downHosts():
    monthPickerStart = ""
    monthPickerEnd = ""
    selectTimeOver = 1440
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    formatted_date = f"{current_year}-{current_month:02d}"
    monthPickerStart = formatted_date
    monthPickerEnd = formatted_date

    if request.method == 'POST':
        monthPickerStart = request.form.get('monthPickerStart')
        monthPickerEnd = request.form.get('monthPickerEnd')
        selectTimeOver = int(request.form.get('selectTimeOver'))

    start_year, start_month = map(int, monthPickerStart.split('-'))
    end_year, end_month = map(int, monthPickerEnd.split('-'))
    host_data_down_over24, count_host_data_name, all_count_down = get_host_down_select_time(start_month, start_year, end_month, end_year, selectTimeOver)

    return render_template("/admin/downHosts.html", title="Down hosts", monthPickerStart=monthPickerStart, monthPickerEnd=monthPickerEnd, host_down_list=host_data_down_over24, all_count_down=all_count_down, selectTimeOver=selectTimeOver)


@admin_module.route("/down-access-points", methods=["GET", "POST"])
@acl.roles_required("admin")
def downAccessPoints():
    monthPickerStart = ""
    monthPickerEnd = ""
    selectTimeOver = 1440
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    formatted_date = f"{current_year}-{current_month:02d}"
    monthPickerStart = formatted_date
    monthPickerEnd = formatted_date

    if request.method == 'POST':
        monthPickerStart = request.form.get('monthPickerStart')
        monthPickerEnd = request.form.get('monthPickerEnd')
        selectTimeOver = int(request.form.get('selectTimeOver'))

    start_year, start_month = map(int, monthPickerStart.split('-'))
    end_year, end_month = map(int, monthPickerEnd.split('-'))
    accessPoint_data_down_over24, count_accessPoint_data_name, all_count_down = get_accessPoint_down_select_time(start_month, start_year, end_month, end_year, selectTimeOver)

    return render_template("/admin/downAccessPoint.html", title="Down Access Points", monthPickerStart=monthPickerStart, monthPickerEnd=monthPickerEnd, accessPoint_down_list=accessPoint_data_down_over24, all_count_down=all_count_down, selectTimeOver=selectTimeOver)
