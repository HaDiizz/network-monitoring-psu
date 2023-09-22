from flask import render_template
from app.views.admin import admin_module
from ... import acl
from ...dash.host_monthly import dash_host
import calendar
from ... import models
from mongoengine import Q

@admin_module.route("/hosts")
@acl.roles_required("admin")
def host():
    return render_template("/admin/host/index.html", title="Host", dash_host=dash_host.index())

@admin_module.route("/hosts/<int:year>/<string:month>")
@acl.roles_required("admin")
def host_quarterly(year, month):
    
    avg_sla , month_name = get_month(int(month),int(year))
    card_tiltle = month_name
    print(month_name , avg_sla)
    return render_template("/admin/host/quarterly.html", title="Host Quarterly", month_name=month_name , avg_sla=avg_sla)

def get_name_month(selected_month,selected_year) :
    if selected_month + 2 <=  12  :
        start_month = calendar.month_name[selected_month]
        end_month  = calendar.month_name[selected_month+2]
        card_tittle = start_month + " " + str(selected_year) + " to "+ end_month  + " " + str(selected_year)
    elif selected_month + 2 ==  13  :
        start_month = calendar.month_name[selected_month]
        end_month  = calendar.month_name[1]
        card_tittle = start_month + " " + str(selected_year) + " to "+ end_month  + " " + str(selected_year + 1)
    elif selected_month + 2 ==  14  :
        start_month = calendar.month_name[selected_month]
        end_month  = calendar.month_name[2]
        card_tittle = start_month + " " + str(selected_year) + " to "+ end_month  + " " + str(selected_year + 1)
    return card_tittle

def search_month(start_month,end_month,selected_year)   :
    if end_month  == 13:
        print("working")
        query = models.Host.objects(
            (Q(month=11) & Q(year=selected_year)) | (Q(month=12) & Q(year=selected_year)) | (Q(month=1) & Q(year=selected_year + 1))
        )
        return query
    elif end_month  == 14:
        query = models.Host.objects(
            (Q(month=12) & Q(year=selected_year)) | (Q(month=1) & Q(year=selected_year  + 1)) | (Q(month=2) & Q(year=selected_year + 1))
        )
        return query

def get_month(selected_month,selected_year):
    start_month = selected_month
    end_month = selected_month + 2
    print(selected_month , selected_year)
    avg_sla = 0
    count = 0
    
    if end_month > 12:
        query = search_month(start_month,end_month,selected_year)
        matching_hosts = query.all()

        print("many of data : ",len(matching_hosts))
        for host in matching_hosts:

            avg_sla += host.availability
            count  += 1

    else :
        query = models.Host.objects(
            month__gte=start_month,
            month__lte=end_month,
            year__in=[selected_year]
        )
        matching_hosts = query.all()
        print("Len of data : " , len(matching_hosts))
        for host in matching_hosts:
            avg_sla += host.availability
            count  += 1
            
    if avg_sla != 0 :
        avg_sla = avg_sla  / count
        print("AVG_SLA  : " , avg_sla)    
        
    Card_tittle = get_name_month(selected_month,selected_year)    
    print("New line\n")
    return  avg_sla,Card_tittle
