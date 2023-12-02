from flask import render_template
from app.views.admin import admin_module
from ... import acl
from ...dash.host_monthly import dash_host
import calendar
from ...helpers.utils import get_day_data, get_quarter_data, sla_status_list
from ... import models


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
    avg_sla, host_all_count, host_name, host_sla, host_ip, host_count, month_name, host_sla_first_month, host_sla_second_month, host_sla_third_month, host_count_first_month, host_count_second_month, host_count_third_month, host_count_sum_first_month, host_count_sum_second_month, host_count_sum_third_month, host_sla_sum_first_month, host_sla_sum_second_month, host_sla_sum_third_month = get_quarter_data(
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
    
    host_data_first_month = {host_name[i]: {"host_name": host_name[i], "host_sla": host_sla_first_month[i],
                                "host_ip": host_ip[i], "host_count": host_count_first_month[i]} for i in range(len(host_name))} 
    
    if len(host_sla_second_month) == 0 :
        host_data_second_month = {}
    else :
        host_data_second_month = {host_name[i]: {"host_name": host_name[i], "host_sla": host_sla_second_month[i],
                                    "host_ip": host_ip[i], "host_count": host_count_second_month[i]} for i in range(len(host_name))} 
    if len(host_sla_third_month) == 0 :
        host_data_third_month = {}
    else :
        host_data_third_month = {host_name[i]: {"host_name": host_name[i], "host_sla": host_sla_third_month[i],
                                    "host_ip": host_ip[i], "host_count": host_count_third_month[i]} for i in range(len(host_name))} 
    
    # table_data = {
    #     "quarterly": {
    #         "host_data": host_data
    #         "avg_sla": avg_sla,
    #         "host_all_count": host_all_count,
    #     },
    #     "first_month": {
    #         "host_data": host_sla_first_month
    #     }
    # }
    
    
    # print('host_sla_first_month', host_sla_first_month)
    
    return render_template("/admin/host/quarterly.html", title="Host Quarterly", month_name=month_name, host_data=host_data, host_all_count=host_all_count, avg_sla=round(avg_sla, 2), day_data=day_data, months=months, sla_status=sla_status, host_sla_first_month=host_sla_first_month, host_sla_second_month=host_sla_second_month, host_sla_third_month=host_sla_third_month, host_count_first_month=host_count_first_month, host_count_second_month=host_count_second_month, host_count_third_month=host_count_third_month, host_count_sum_first_month=host_count_sum_first_month, host_count_sum_second_month=host_count_sum_second_month, host_count_sum_third_month=host_count_sum_third_month, host_sla_sum_first_month=host_sla_sum_first_month, host_sla_sum_second_month=host_sla_sum_second_month, host_sla_sum_third_month=host_sla_sum_third_month)
