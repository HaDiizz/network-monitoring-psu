from flask import render_template
from app.views.admin import admin_module
from ... import acl
from ...dash.service_monthly import dash_service
import calendar
from ...helpers.utils import sla_status_list, get_service_quarter_data, get_day_data
from ... import models
from app import caches


@admin_module.route("/services")
@acl.roles_required("admin")
def service():
    return render_template("/admin/service/index.html", title="Service", dash_service=dash_service.index())


@admin_module.route("/services/<int:year>/<string:month>")
@acl.roles_required("admin")
@caches.cache.cached(timeout=3600, key_prefix='service_quarterly')
def service_quarterly(year, month):
    sla_requirement = models.SLAConfig.objects(year=year, category="Service").first()
    sla_status = sla_status_list()
    if sla_requirement:
        sla_status = {
        "ok_status": sla_requirement["ok_status"],
        "warning_status": sla_requirement["warning_status"],
        "critical_status": sla_requirement["critical_status"]
        }
    avg_sla, service_all_count, service_name, service_sla, service_count, month_name, service_sla_first_month, service_sla_second_month, service_sla_third_month, service_count_first_month, service_count_second_month, service_count_third_month, service_count_sum_first_month, service_count_sum_second_month, service_count_sum_third_month, service_sla_sum_first_month, service_sla_sum_second_month, service_sla_sum_third_month = get_service_quarter_data(
        int(month), int(year))
    day_data = get_day_data(int(month), int(year), "service")
    months = {}
    if day_data:
        for key in day_data.keys():
            month_number = int(key.split('-')[1])
            month_name_str = calendar.month_name[month_number]
            months[month_name_str] = str(month_number)
    service_data = {service_name[i]: {"service_name": service_name[i], "service_sla": '{:.4f}'.format(round( service_sla[i], 8)),
                                "service_count": service_count[i]} for i in range(len(service_name))}
    service_data_first_month = {service_name[i]: {"service_name": service_name[i], "service_sla": '{:.4f}'.format(round( service_sla_first_month[i], 8)),
                                "service_count": service_count_first_month[i]} for i in range(len(service_name))} 
    
    if len(service_sla_second_month) == 0 :
        service_data_second_month = {}
    else :
        service_data_second_month = {service_name[i]: {"service_name": service_name[i], "service_sla": '{:.4f}'.format(round( service_sla_second_month[i], 8)),
                                    "service_count": service_count_second_month[i]} for i in range(len(service_name))} 
    if len(service_sla_third_month) == 0 :
        service_data_third_month = {}
    else :
        service_data_third_month = {service_name[i]: {"service_name": service_name[i], "service_sla": '{:.4f}'.format(round( service_sla_third_month[i], 8)),
                                    "service_count": service_count_third_month[i]} for i in range(len(service_name))} 

    month_list_quarterly = list(months.keys())

    table_data = {
        "Quarterly": {
            "service_data": service_data,
            "avg_sla": '{:.4f}'.format(round(avg_sla, 8)),
            "service_all_count": service_all_count
        }
    }

    if len(month_list_quarterly) >= 1:
        table_data[month_list_quarterly[0]] = {
            "service_data": service_data_first_month,
            "avg_sla": '{:.4f}'.format(round(service_sla_sum_first_month, 8)),
            "service_all_count": service_count_sum_first_month
        }

    if len(month_list_quarterly) >= 2:
        table_data[month_list_quarterly[1]] = {
            "service_data": service_data_second_month,
            "avg_sla": '{:.4f}'.format(round(service_sla_sum_second_month, 8)),
            "service_all_count": service_count_sum_second_month
        }

    if len(month_list_quarterly) >= 3:
        table_data[month_list_quarterly[2]] = {
            "service_data": service_data_third_month,
            "avg_sla": '{:.4f}'.format(round(service_sla_sum_third_month, 8)),
            "service_all_count": service_count_sum_third_month
        }
    return render_template("/admin/service/quarterly.html", title="Service Quarterly", month_name=month_name, day_data=day_data, months=months, sla_status=sla_status,table_data=table_data)