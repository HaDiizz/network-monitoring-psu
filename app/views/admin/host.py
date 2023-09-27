from flask import render_template
from app.views.admin import admin_module
from ... import acl
from ...dash.host_monthly import dash_host
import calendar
from ...helpers.utils import get_day_data, get_quarter_data


@admin_module.route("/hosts")
@acl.roles_required("admin")
def host():
    return render_template("/admin/host/index.html", title="Host", dash_host=dash_host.index())


@admin_module.route("/hosts/<int:year>/<string:month>")
@acl.roles_required("admin")
def host_quarterly(year, month):
    avg_sla, host_all_count, host_name, host_sla, host_ip, host_count, month_name = get_quarter_data(
        int(month), int(year))
    day_data = get_day_data(int(month), int(year))

    months = {}
    if day_data:
        for key in day_data.keys():
            month_number = int(key.split('-')[1])
            month_name = calendar.month_name[month_number]
            months[month_name] = str(month_number)
    host_data = {host_name[i]: {"host_name": host_name[i], "host_sla": host_sla[i],
                                "host_ip": host_ip[i], "host_count": host_count[i]} for i in range(len(host_name))}
    return render_template("/admin/host/quarterly.html", title="Host Quarterly", month_name=month_name, host_data=host_data, host_all_count=host_all_count, avg_sla=round(avg_sla, 2), day_data=day_data, months=months,)
