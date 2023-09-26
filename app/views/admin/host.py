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
    avg_sla , host_all_count, host_name, host_sla , host_ip, host_count,month_name = get_quarter_data(int(month),int(year))
    day_data =  get_day_data(int(month),int(year))
    # months = set() if not day_data else set(calendar.month_name[int(key.split('-')[1])] for key in day_data.keys())
    months = {}
    if day_data:
        for key in day_data.keys():
            month_number = int(key.split('-')[1])
            month_name = calendar.month_name[month_number]
            months[month_name] = str(month_number)
    # months_number = set() if not day_data else set(key.split('-')[1] for key in day_data.keys())
    card_title = month_name
    host_data = {host_name[i]: {"host_name": host_name[i], "host_sla": host_sla[i] , "host_ip": host_ip[i] , "host_count": host_count[i]} for i in range(len(host_name))} 
    return render_template("/admin/host/quarterly.html", title="Host Quarterly", month_name=month_name , host_data = host_data, host_all_count = host_all_count , avg_sla = round(avg_sla, 2) ,day_data = day_data, months=months,)

def get_name_month(selected_month, selected_year) :
    if selected_month + 2 <=  12  :
        start_month = calendar.month_name[selected_month]
        end_month  = calendar.month_name[selected_month+2]
        card_title = start_month + " " + str(selected_year) + " to "+ end_month  + " " + str(selected_year)
    elif selected_month + 2 ==  13  :
        start_month = calendar.month_name[selected_month]
        end_month  = calendar.month_name[1]
        card_title = start_month + " " + str(selected_year) + " to "+ end_month  + " " + str(selected_year + 1)
    elif selected_month + 2 ==  14  :
        start_month = calendar.month_name[selected_month]
        end_month  = calendar.month_name[2]
        card_title = start_month + " " + str(selected_year) + " to "+ end_month  + " " + str(selected_year + 1)
    return card_title

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
        query = models.Host.objects(
            (Q(host_id= host_name) & Q(month=11) & Q(year=selected_year)) | Q(host_id= host_name) & (Q(month=12) & Q(year=selected_year)) | Q(host_id= host_name) & (Q(month=1) & Q(year=selected_year + 1))
        )
        return query
    elif end_month  == 14:
        query = models.Host.objects(
            (Q(host_id= host_name) & Q(month=12) & Q(year=selected_year)) | Q(host_id= host_name) & (Q(month=1) & Q(year=selected_year  + 1)) | Q(host_id= host_name) & (Q(month=2) & Q(year=selected_year + 1))
        )
        return query
    
def search_day_data(matching_data):
    host_day_dict = []
    for data in matching_data:
            print(data.created_date)
            day = data.created_date.day
            month = data.created_date.month
            day = str(day) + "-" + str(month)
            if host_day_dict :
                for check_day in host_day_dict :
                    day_exists = any(check_day["day"] == day for check_day in host_day_dict)
                    if day_exists:
                        if check_day["day"] == day:
                            print("Day : ", check_day["day"],"COUNT : ",check_day["count"] , "SUM : " ,check_day["time"])
                            check_day["time"] =  check_day["time"] + data.minutes
                            check_day["count"] =  check_day["count"] + 1
                            print("After : ","Day : ", check_day["day"],"COUNT : ",check_day["count"] , "SUM : " ,check_day["time"])
                            break
            
                    else :
                        date = day
                        time = data.minutes
                        count = 1
                        start_day = {"day": day, "time": time, "count": count}
                        host_day_dict.append(start_day)
                        break
                
                        
            else :
                date = day
                time = data.minutes
                count = 1
                start_day = {"day": day, "time": time, "count": count}
                host_day_dict.append(start_day)
            print(host_day_dict)
            print("\n")
    print(host_day_dict)
    return host_day_dict

def get_day_data(selected_month,selected_year):
    start_month = selected_month
    end_month = selected_month + 2
    if end_month > 12:
        query = search_month(start_month,end_month,selected_year)
    else :
        query = search_month(start_month,end_month,selected_year)    
    
    host = query.all()
    
    host_list_id = []
    if host :
        for hosts in host :
            for value in hosts.host_list:
                if value.last_state != -1:
                    print(value.id)
                    host_list_id.append(value.id)

        query  = models.HostList.objects(id__in=host_list_id)
        matching_data = query.all()
        host_day_dict = search_day_data(matching_data)
        data_dict = {item['day']: {"date": item['day'], 'sla': round((1440 - (item['time']/item['count']))/1440 * 100, 2)} for item in host_day_dict}
        return data_dict
                            
    

def get_quarter_data(selected_month,selected_year):
    start_month = selected_month
    end_month = selected_month + 2
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
    card_title = get_name_month(selected_month,selected_year)    
    return  avg_sla,host_all_count, host_name, host_sla, host_ip, host_count, card_title
