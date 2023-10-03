from flask import Blueprint, render_template
from ... import acl
from ...helpers.api import host_list, service_list, host_group, host_group_list, service_group_list, maintain_host_list
from ...helpers.utils import location_list
import os
from app import caches
admin_module = Blueprint("admin", __name__, url_prefix="/admin")

from app.views.admin.service import *
from app.views.admin.host import *
from app.views.admin.management import *

PSU_CORE_NETWORK = f"{os.environ['PSU_CORE_NETWORK']}"
PSU_HATYAI_CAMPUS_NETWORK = f"{os.environ['PSU_HATYAI_CAMPUS_NETWORK']}"
PSU_HAT_YAI_WIRELESS = f"{os.environ['PSU_HAT_YAI_WIRELESS']}"
GROUP_CHECK_MK = f"{os.environ['GROUP_CHECK_MK']}"
OUTSIDE_PSU = f"{os.environ['OUTSIDE_PSU']}"

WEB_SERVICE_GROUP = f"{os.environ['WEB_SERVICE_GROUP']}"
AD_SERVICE_GROUP = f"{os.environ['AD_SERVICE_GROUP']}"

@admin_module.route("/overview")
@acl.roles_required("admin")
@caches.cache.cached(timeout=3600, key_prefix='overview')
def index():
    hosts = host_list()
    web_service = service_list(api_service_url=WEB_SERVICE_GROUP)
    services = web_service
    host_groups = host_group_list()
    service_groups = service_group_list()
    maintain_hosts = maintain_host_list()
    psu_core_network_group = host_group(api_hostgroup_url=PSU_CORE_NETWORK)
    psu_hatyai_campus_network = host_group(api_hostgroup_url=PSU_HATYAI_CAMPUS_NETWORK)
    psu_hat_yai_wireless = host_group(api_hostgroup_url=PSU_HAT_YAI_WIRELESS)
    check_mk_group = host_group(api_hostgroup_url=GROUP_CHECK_MK)
    outside_psu = host_group(api_hostgroup_url=OUTSIDE_PSU)

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
            else:
                service_state = "UNKNOWN" 
            if service_state not in service_summary:
                service_summary[service_state] = 0
            service_summary[service_state] += 1
        service_summary["TOTAL"] = len(services)
    return render_template("/admin/index.html", title="Overview", location_list=location_list(), host_list=hosts, service_list=services, host_summary=host_summary, service_summary=service_summary, host_group_list=host_groups, service_group_list=service_groups)
