from flask import render_template
from app.views.admin import admin_module
from ... import acl
from ...dash.host_monthly import dash_host
from ...dash.host_quarterly import dash_host_quarterly, dash
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
    dash.ctx.set("year", year)
    dash.ctx.set("month", month)
    avg_sla , host_all_count, host_name, host_sla , host_ip, host_count,month_name = get_data(int(month),int(year))
    card_tiltle = month_name
    host_detail = {host_name[i]: {"host_sla": host_sla[i] , "host_ip": host_ip[i] , "host_count": host_count[i]} for i in range(len(host_name))} 
    print(host_detail)
    return render_template("/admin/host/quarterly.html", title="Host Quarterly", month_name=month_name , host_detail = host_detail, host_all_count = host_all_count , avg_sla=avg_sla)

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
    if end_month  <= 12:
        query = models.Host.objects(
            month__gte=start_month,
            month__lte=end_month,
            year__in=[selected_year]
        )
        return query
    elif end_month  == 13:
        query = models.Host.objects(
            (Q(month=11) & Q(year=selected_year)) | (Q(month=12) & Q(year=selected_year)) | (Q(month=1) & Q(year=selected_year + 1))
        )
        return query
    elif end_month  == 14:
        query = models.Host.objects(
            (Q(month=12) & Q(year=selected_year)) | (Q(month=1) & Q(year=selected_year  + 1)) | (Q(month=2) & Q(year=selected_year + 1))
        )
        return query

def search_host(start_month,end_month,selected_year, host_name)   :
    if end_month <= 12:
        query = models.Host.objects(
                host_id = host_name,
                month__gte=start_month,
                month__lte=end_month,
                year__in=[selected_year])
        return query
    if end_month  == 13:
        print("working")
        query = models.Host.objects(
            (Q(host_id= host_name) & Q(month=11) & Q(year=selected_year)) | Q(host_id= host_name) & (Q(month=12) & Q(year=selected_year)) | Q(host_id= host_name) & (Q(month=1) & Q(year=selected_year + 1))
        )
        return query
    elif end_month  == 14:
        query = models.Host.objects(
            (Q(host_id= host_name) & Q(month=12) & Q(year=selected_year)) | Q(host_id= host_name) & (Q(month=1) & Q(year=selected_year  + 1)) | Q(host_id= host_name) & (Q(month=2) & Q(year=selected_year + 1))
        )
        return query

def get_data(selected_month,selected_year):
    start_month = selected_month
    end_month = selected_month + 2
    print(selected_month , selected_year)
    avg_sla = 0
    count = 0
    host_all_count = 0
    host_name = []
    host_sla = []
    host_ip = []
    host_count = []
    
    if end_month > 12:
        query = search_month(start_month,end_month,selected_year)
        matching_hosts = query.all()

        
        for host in matching_hosts:

            avg_sla += host.availability
            host_all_count += host.count
            print("Host name : ", host.host_id , " count : " , host.count ," month : ", host.month)
            count  += 1

            
            if host.name in host_name :
                continue
            else :
                host_name.append(host.name)
            
        for host in host_name :
            query = search_host(start_month,end_month,selected_year, host)
            matching_hosts = query.all()
            sla = 0
            count_down = 0
            for host in matching_hosts:
                sla += host.availability
                count_down += host.count

                if host.ip_address in host_ip :
                    continue
                else :
                    host_ip.append(host.ip_address)

            sla = sla / len(matching_hosts)
            host_sla.append(sla)
            host_count.append(count_down)
    else :
        query = search_month(start_month,end_month,selected_year)
        matching_hosts = query.all()

        for host in matching_hosts:
            avg_sla += host.availability
            host_all_count += host.count
            count  += 1
            print("Host name : ", host.host_id , " count : " , host.count ," month : ", host.month , " sum of count : " , host_all_count)
            
            
            if host.name in host_name :
                continue
            else :
                host_name.append(host.name)

        for host in host_name :
            
            query = search_host(start_month,end_month,selected_year, host)

            matching_hosts = query.all()
            sla = 0
            count_down = 0
            for host in matching_hosts:
                sla += host.availability
                count_down += host.count

                if host.ip_address in host_ip :
                    continue
                else :
                    host_ip.append(host.ip_address)

            sla = sla / len(matching_hosts)
            host_sla.append(sla)
            host_count.append(count_down)

            

    if avg_sla != 0 :
        avg_sla = avg_sla  / count
        print("AVG_SLA  : " , avg_sla)    
        
    Card_tittle = get_name_month(selected_month,selected_year)    
    print("New line\n")
    return  avg_sla,host_all_count, host_name, host_sla, host_ip, host_count,Card_tittle
