from flask import render_template
from nwms.web.views.admin import admin_module
from nwms.web import acl
from nwms.web.dash.host_monthly import dash_host
import calendar
from nwms.web.helpers.utils import get_day_data, get_quarter_data, sla_status_list
from nwms import models


@admin_module.route("/hosts")
@acl.roles_required("admin")
def host():
    return render_template("/admin/host/index.html", title="Host", dash_host=dash_host.index())


@admin_module.route("/hosts/<int:year>/<string:month>")
@acl.roles_required("admin")
def host_quarterly(year, month):
    sla_requirement = models.SLAConfig.objects(year=year).first()
    sla_status = sla_status_list()
    if sla_requirement:
        sla_status = {
        "ok_status": sla_requirement["ok_status"],
        "warning_status": sla_requirement["warning_status"],
        "critical_status": sla_requirement["critical_status"]
        }
    avg_sla, host_all_count, host_name, host_sla, host_ip, host_count, month_name = get_quarter_data(
        int(month), int(year))
    day_data = get_day_data(int(month), int(year))

    months = {}
    if day_data:
        for key in day_data.keys():
            month_number = int(key.split('-')[1])
            month_name_str = calendar.month_name[month_number]
            months[month_name_str] = str(month_number)
    host_data = {host_name[i]: {"host_name": host_name[i], "host_sla": host_sla[i],
                                "host_ip": host_ip[i], "host_count": host_count[i]} for i in range(len(host_name))}
    return render_template("/admin/host/quarterly.html", title="Host Quarterly", month_name=month_name, host_data=host_data, host_all_count=host_all_count, avg_sla=round(avg_sla, 2), day_data=day_data, months=months, sla_status=sla_status)