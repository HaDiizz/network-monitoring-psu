from flask import render_template
from app.views.admin import admin_module
from ... import acl
from ...dash.host_monthly import dash_host
import calendar
from ...helpers.utils import get_day_data, get_host_quarter_data, sla_status_list
from ... import models
from app import caches


@admin_module.route("/hosts")
@acl.roles_required("admin")
def host_history():
    return render_template("/admin/host/index.html", title="Host", dash_host=dash_host.index())


@admin_module.route("/hosts/<int:year>/<string:month>")
@acl.roles_required("admin")
@caches.cache.cached(timeout=3600)
def host_quarterly(year, month):
    sla_requirement = models.SLAConfig.objects(year=year, category="Host").first()
    sla_status = sla_status_list()
    if sla_requirement:
        sla_status = {
        "ok_status": float(sla_requirement["ok_status"]),
        "critical_status": float(sla_requirement["critical_status"])
        }
    avg_sla, host_all_count, host_name, host_sla, host_ip, host_count, month_name, host_sla_first_month, host_sla_second_month, host_sla_third_month, host_count_first_month, host_count_second_month, host_count_third_month, host_count_sum_first_month, host_count_sum_second_month, host_count_sum_third_month, host_sla_sum_first_month, host_sla_sum_second_month, host_sla_sum_third_month, host_name_first_month, host_name_second_month, host_name_third_month = get_host_quarter_data(
        int(month), int(year))
    day_data = get_day_data(int(month), int(year), "host")
    months = {}
    if day_data:
        for key in day_data.keys():
            month_number = int(key.split('-')[1])
            month_name_str = calendar.month_name[month_number]
            months[month_name_str] = str(month_number)
    host_data = {host_name[i]: {"host_name": host_name[i], "host_sla": '{:.4f}'.format(round( host_sla[i], 4)),
                                "host_ip": host_ip[i], "host_count": host_count[i]} for i in range(len(host_name))}
    print("TEST")
    print(len(host_name))
    print(len(host_sla_first_month))
    print(len(host_ip))
    print(len(host_count_first_month))
    
    host_data_first_month = {host_name[i]: {"host_name": host_name[i], "host_sla": '{:.4f}'.format(round( host_sla_first_month[i], 4)),
                                "host_ip": host_ip[i], "host_count": host_count_first_month[i]} for i in range(len(host_name_first_month))} 
    
    if len(host_sla_second_month) == 0 :
        host_data_second_month = {}
    else :
        host_data_second_month = {host_name_second_month[i]: {"host_name": host_name_second_month[i], "host_sla": '{:.4f}'.format(round( host_sla_second_month[i], 4)),
                                    "host_ip": host_ip[i], "host_count": host_count_second_month[i]} for i in range(len(host_name_second_month))} 
    if len(host_sla_third_month) == 0 :
        host_data_third_month = {}
    else :
        host_data_third_month = {host_name_third_month[i]: {"host_name": host_name_third_month[i], "host_sla": '{:.4f}'.format(round( host_sla_third_month[i], 4)),
                                    "host_ip": host_ip[i], "host_count": host_count_third_month[i]} for i in range(len(host_name_third_month))} 

    month_list_quarterly = list(months.keys())

    table_data = {
        "Quarterly": {
            "host_data": host_data,
            "avg_sla": '{:.4f}'.format(round(avg_sla, 4)),
            "host_all_count": host_all_count
        }
    }

    if len(month_list_quarterly) >= 1:
        table_data[month_list_quarterly[0]] = {
            "host_data": host_data_first_month,
            "avg_sla": '{:.4f}'.format(round(host_sla_sum_first_month, 4)),
            "host_all_count": host_count_sum_first_month
        }

    if len(month_list_quarterly) >= 2:
        table_data[month_list_quarterly[1]] = {
            "host_data": host_data_second_month,
            "avg_sla": '{:.4f}'.format(round(host_sla_sum_second_month, 4)),
            "host_all_count": host_count_sum_second_month
        }

    if len(month_list_quarterly) >= 3:
        table_data[month_list_quarterly[2]] = {
            "host_data": host_data_third_month,
            "avg_sla": '{:.4f}'.format(round(host_sla_sum_third_month, 4)),
            "host_all_count": host_count_sum_third_month
        }
    return render_template("/admin/host/quarterly.html", title="Host Quarterly", month_name=month_name, day_data=day_data, months=months, sla_status=sla_status,table_data=table_data)
