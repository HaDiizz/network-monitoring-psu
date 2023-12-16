from flask import Blueprint, render_template, jsonify
from ... import acl
from ...helpers.api import host_list, service_list, host_group, host_group_list, service_group_list, maintain_host_list, maintain_service_list, service_down_handler, service_is_down, host_is_down, host_down_handler, accessPoint_down_handler
from ...helpers.utils import location_list
from ...helpers.utils import get_host_down_over24h
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
    services = service_list("ALL")
    host_groups = host_group_list()
    service_groups = service_group_list()
    maintain_hosts = maintain_host_list()
    maintain_services = maintain_service_list()

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
    return render_template("/admin/index.html", title="Overview", location_list=location_list(), host_list=hosts, service_list=services, host_summary=host_summary, service_summary=service_summary, host_group_list=host_groups, service_group_list=service_groups)


@admin_module.route("/test")
def test():
    service_down_list = service_is_down()
    # ! ถ้าอยากดูข้อมูล service_down_list ให้ uncomment
    # return jsonify(service_is_down())
    # return jsonify(host_is_down())
    return jsonify(accessPoint_down_handler())

@admin_module.route("/down-hosts", methods=["GET", "POST"])
@acl.roles_required("admin")
def downHosts():
    monthPickerStart = ""
    monthPickerEnd = ""
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    formatted_date = f"{current_year}-{current_month:02d}"
    monthPickerStart = formatted_date
    monthPickerEnd = formatted_date
    start_year, start_month = map(int, formatted_date.split('-'))
    end_year, end_month = map(int, formatted_date.split('-'))
    host_data_down_over24, count_host_data_name, all_count_down = get_host_down_over24h(start_month, start_year, end_month, end_year)
    if request.method == 'POST':
        monthPickerStart = request.form.get('monthPickerStart')
        monthPickerEnd = request.form.get('monthPickerEnd')

        start_year, start_month = map(int, monthPickerStart.split('-'))
        end_year, end_month = map(int, monthPickerEnd.split('-'))
        host_data_down_over24, count_host_data_name, all_count_down = get_host_down_over24h(start_month, start_year, end_month, end_year)

    return render_template("/admin/downHosts.html", title="Down hosts", monthPickerStart=monthPickerStart, monthPickerEnd=monthPickerEnd, host_down_list=host_data_down_over24, all_count_down=all_count_down)
