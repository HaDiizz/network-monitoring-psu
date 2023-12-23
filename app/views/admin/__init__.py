from flask import Blueprint, render_template, jsonify
from ... import acl
from ...helpers.api import host_list, service_list, host_group, host_group_list, service_group_list, maintain_host_list, maintain_service_list, service_down_handler, service_is_down, host_is_down, host_down_handler, accessPoint_down_handler, access_point_list, get_all_service_list, access_point_list
from ...helpers.utils import location_list, get_host_down_select_time, get_all_ap_list, get_ap_list_with_sla
from app import caches
import datetime

admin_module = Blueprint("admin", __name__, url_prefix="/admin")

from app.views.admin.service import *
from app.views.admin.host import *
from app.views.admin.management import *


@admin_module.route("/overview")
@acl.roles_required("admin")
# @caches.cache.cached(timeout=3600, key_prefix='overview')
def index():
    hosts = host_list()
    services = get_all_service_list()
    host_groups = host_group_list()
    service_groups = service_group_list(False)
    maintain_hosts = maintain_host_list()
    maintain_services = maintain_service_list()
    
    accessPoints_resp = access_point_list()
    if accessPoints_resp is None:
        accessPoints_resp = []
    accessPoints = get_all_ap_list(accessPoints_resp)

    if not host_groups:
        host_groups = []
    if not service_groups:
        service_groups = []
    if not services:
        services = []
    if not hosts:
        hosts = []
    host_summary = {}
    service_summary = {}
    accessPoint_summary = {}
    if hosts:
        for host in hosts:
            host_last_state = host["extensions"]["last_state"]
            if host_last_state == 0:
                host_state = "UP"
            elif host_last_state == 1:
                host_state = "DOWN"
            elif host_last_state == 2:
                host_state = "UNREACH"
            for maintain_host in maintain_hosts:
                if host["id"] == maintain_host["id"]:
                    host_state = "MAINTAIN"
            if host_state not in host_summary:
                host_summary[host_state] = 0
            host_summary[host_state] += 1
        host_summary["TOTAL"] = len(hosts)
    if services:
        for service in services:
            service_last_state = service["extensions"]["state"]
            if service_last_state == 0:
                service_state = "OK" 
            elif service_last_state == 1:
                service_state = "WARN"
            elif service_last_state == 2:
                service_state = "CRIT"
            elif service_last_state == 3:
                service_state = "UNKNOWN" 
            for maintain_service in maintain_services:
                if service["id"] == maintain_service["id"]:
                    service_state = "MAINTAIN"
            if service_state not in service_summary:
                service_summary[service_state] = 0
            service_summary[service_state] += 1
        service_summary["TOTAL"] = len(services)
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
            # for maintain_accessPoint in maintain_accessPoints:
            #     if accessPoint["id"] == maintain_accessPoint["id"]:
            #         accessPoint_state = "MAINTAIN"
            if accessPoint_state not in accessPoint_summary:
                accessPoint_summary[accessPoint_state] = 0
            accessPoint_summary[accessPoint_state] += 1
        accessPoint_summary["TOTAL"] = len(accessPoints)
    return render_template("/admin/index.html", title="Overview", location_list=location_list(), host_list=hosts, service_list=services, host_summary=host_summary, service_summary=service_summary, host_group_list=host_groups, service_group_list=service_groups, access_point_list=accessPoints, accessPoint_summary=accessPoint_summary)


@admin_module.route("/overview/access-point")
@acl.roles_required("admin")
# @caches.cache.cached(timeout=3600, key_prefix='access_point_dashboard')
def access_point_dashboard():
    accessPoints_resp = access_point_list()
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
            if accessPoint_state not in accessPoint_summary:
                accessPoint_summary[accessPoint_state] = 0
            accessPoint_summary[accessPoint_state] += 1
        accessPoint_summary["TOTAL"] = len(accessPoints)
    return render_template("/admin/overview/accessPoint.html", title="AccessPoint", location_list=location_list(), accessPoint_summary=accessPoint_summary, access_point_list=accessPoints)


@admin_module.route("/overview/host")
@acl.roles_required("admin")
@caches.cache.cached(timeout=10800, key_prefix='host_dashboard')
def host_dashboard():
    hosts = host_list()
    host_groups = host_group_list()
    maintain_hosts = maintain_host_list()

    if not host_groups:
        host_groups = []
    if not hosts:
        hosts = []
    host_summary = {}
    if hosts:
        for host in hosts:
            host_state = host["extensions"]["state"]
            if host_state == 0:
                host_state = "UP"
            elif host_state == 1:
                host_state = "DOWN"
            elif host_state == 2:
                host_state = "UNREACH"
            for maintain_host in maintain_hosts:
                if host["id"] == maintain_host["id"]:
                    host_state = "MAINTAIN"
                    host["extensions"]["state"] = -1
            if host_state not in host_summary:
                host_summary[host_state] = 0
            host_summary[host_state] += 1
        host_summary["TOTAL"] = len(hosts)
    return render_template("/admin/overview/host.html", title="Host", location_list=location_list(), host_list=hosts, host_summary=host_summary, host_group_list=host_groups)


@admin_module.route("/overview/service")
@acl.roles_required("admin")
@caches.cache.cached(timeout=10800, key_prefix='service_dashboard')
def service_dashboard():
    services = get_all_service_list()
    service_groups = service_group_list(True)
    maintain_services = maintain_service_list()
    
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
    return render_template("/admin/overview/service.html", title="Service", service_list=services, service_summary=service_summary, service_group_list=service_groups)

@admin_module.route("/test")
def test():
    service_down_list = service_is_down()
    get_ap_data = access_point_list()
    result = get_all_ap_list(get_ap_data)
    # ! ถ้าอยากดูข้อมูล service_down_list ให้ uncomment
    # return jsonify(service_is_down())
    # return jsonify(host_is_down())
    return jsonify(result)

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
