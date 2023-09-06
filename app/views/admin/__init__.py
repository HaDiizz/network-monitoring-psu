from flask import Blueprint, render_template
from ... import acl
from ...utils import location_list, host_list, service_list

admin_module = Blueprint("admin", __name__, url_prefix="/admin")

from app.views.admin.service import *
from app.views.admin.host import *
from app.views.admin.management import *

@admin_module.route("/overview")
@acl.roles_required("admin")
def index():
    hosts = host_list()
    services = service_list()
    if not services:
        services = []
    if not hosts:
        hosts = []
    host_groups_summary = {}
    service_groups_summary = {}
    if hosts:
        for host in hosts:
            host_last_state = host["extensions"]["last_state"]
            host_state = "UP" if host_last_state == 0 else "DOWN"
            if host_state not in host_groups_summary:
                host_groups_summary[host_state] = 0
            host_groups_summary[host_state] += 1
        host_groups_summary["TOTAL"] = len(hosts)
    if services:
        for service in services:
            service_last_state = service["extensions"]["state"]
            if service_last_state == 0:
                service_state = "OK" 
            elif service_last_state == 1:
                service_state = "CRIT"
            else:
                service_state = "WARN" 
            if service_state not in service_groups_summary:
                service_groups_summary[service_state] = 0
            service_groups_summary[service_state] += 1
        service_groups_summary["TOTAL"] = len(services)
    return render_template("/admin/index.html", title="Overview", location_list=location_list(), host_list=hosts, service_list=services, host_groups_summary=host_groups_summary, service_groups_summary=service_groups_summary)
