from flask import render_template
from app.views.admin import admin_module
from ... import acl
from ...dash.access_point_monthly import dash_access_point
import calendar
from ...helpers.utils import sla_status_list, get_accessPoint_quarter_data, get_day_data
from ... import models
from app import caches


@admin_module.route("/access-points")
@acl.roles_required("admin")
def access_point():
    return render_template("/admin/access-point/index.html", title="Access Point", dash_access_point=dash_access_point.index())


@admin_module.route("/access-points/<int:year>/<string:month>")
@acl.roles_required("admin")
@caches.cache.cached(timeout=3600)
def access_point_quarterly(year, month):
    sla_requirement = models.SLAConfig.objects(year=year, category="Access Point").first()
    sla_status = sla_status_list()
    if sla_requirement:
        sla_status = {
        "ok_status": sla_requirement["ok_status"],
        "critical_status": sla_requirement["critical_status"]
        }
    avg_sla, accessPoint_all_count, accessPoint_name, accessPoint_sla, accessPoint_count, month_name, accessPoint_sla_first_month, accessPoint_sla_second_month, accessPoint_sla_third_month, accessPoint_count_first_month, accessPoint_count_second_month, accessPoint_count_third_month, accessPoint_count_sum_first_month, accessPoint_count_sum_second_month, accessPoint_count_sum_third_month, accessPoint_sla_sum_first_month, accessPoint_sla_sum_second_month, accessPoint_sla_sum_third_month, accessPoint_name_second_month , accessPoint_name_third_month = get_accessPoint_quarter_data(
        int(month), int(year))
    day_data = get_day_data(int(month), int(year), "access_point")
    months = {}
    if day_data:
        for key in day_data.keys():
            month_number = int(key.split('-')[1])
            month_name_str = calendar.month_name[month_number]
            months[month_name_str] = str(month_number)
    accessPoint_data = {accessPoint_name[i]: {"accessPoint_name": accessPoint_name[i], "accessPoint_sla": '{:.5f}'.format(round( accessPoint_sla[i], 8)),
                                "accessPoint_count": accessPoint_count[i]} for i in range(len(accessPoint_name))}
    accessPoint_data_first_month = {accessPoint_name[i]: {"accessPoint_name": accessPoint_name[i], "accessPoint_sla": '{:.5f}'.format(round( accessPoint_sla_first_month[i], 8)),
                                "accessPoint_count": accessPoint_count_first_month[i]} for i in range(len(accessPoint_name))} 
    
    if len(accessPoint_sla_second_month) == 0 :
        accessPoint_data_second_month = {}
    else :
        accessPoint_data_second_month = {accessPoint_name_second_month[i]: {"accessPoint_name": accessPoint_name_second_month[i], "accessPoint_sla": '{:.5f}'.format(round( accessPoint_sla_second_month[i], 8)),
                                    "accessPoint_count": accessPoint_count_second_month[i]} for i in range(len(accessPoint_name_second_month))} 
    if len(accessPoint_sla_third_month) == 0 :
        accessPoint_data_third_month = {}
    else :
        accessPoint_data_third_month = {accessPoint_name_third_month[i]: {"accessPoint_name": accessPoint_name_third_month[i], "accessPoint_sla": '{:.5f}'.format(round( accessPoint_sla_third_month[i], 8)),
                                    "accessPoint_count": accessPoint_count_third_month[i]} for i in range(len(accessPoint_name_third_month))} 

    month_list_quarterly = list(months.keys())

    table_data = {
        "Quarterly": {
            "accessPoint_data": accessPoint_data,
            "avg_sla": '{:.5f}'.format(round(avg_sla, 8)),
            "accessPoint_all_count": accessPoint_all_count
        }
    }

    if len(month_list_quarterly) >= 1:
        table_data[month_list_quarterly[0]] = {
            "accessPoint_data": accessPoint_data_first_month,
            "avg_sla": '{:.5f}'.format(round(accessPoint_sla_sum_first_month, 8)),
            "accessPoint_all_count": accessPoint_count_sum_first_month
        }

    if len(month_list_quarterly) >= 2:
        table_data[month_list_quarterly[1]] = {
            "accessPoint_data": accessPoint_data_second_month,
            "avg_sla": '{:.5f}'.format(round(accessPoint_sla_sum_second_month, 8)),
            "accessPoint_all_count": accessPoint_count_sum_second_month
        }

    if len(month_list_quarterly) >= 3:
        table_data[month_list_quarterly[2]] = {
            "accessPoint_data": accessPoint_data_third_month,
            "avg_sla": '{:.5f}'.format(round(accessPoint_sla_sum_third_month, 8)),
            "accessPoint_all_count": accessPoint_count_sum_third_month
        }
    return render_template("/admin/access-point/quarterly.html", title="Access Point Quarterly", month_name=month_name, day_data=day_data, months=months, sla_status=sla_status,table_data=table_data)