from .. import models
from .. import caches
import datetime
import calendar
from mongoengine import Q


def sla_status_list():
    return {
        "ok_status": 99.99,
        "warning_status": 99.5,
        "critical_status": 99
    }


def status_list():
    return [
        'PENDING',
        'CHECKING',
        'COMPLETED',
        'REJECTED',
    ]
    
@caches.cache.cached(timeout=3600, key_prefix='location_list')
def location_list():
    return models.Location.objects().order_by("name")


def cal_min_down(down_time):
    date = datetime.datetime.now()
    current_time = int(date.timestamp())
    time_difference_seconds = current_time - down_time
    time_difference_minute = int(int(time_difference_seconds)/60)
    return time_difference_minute


def cal_sla(month, year, sum_min):
    start_date = datetime.datetime(year, month, 1, 0, 1)
    current_date = datetime.datetime.now()
    time_difference = current_date - start_date
    total_minutes = int(time_difference.total_seconds() / 60)
    sla = ((total_minutes - sum_min)/total_minutes) * 100
    return sla


def get_name_month(selected_month, selected_year):
    if selected_month + 2 <= 12:
        start_month = calendar.month_name[selected_month]
        end_month = calendar.month_name[selected_month+2]
        card_title = start_month + " " + \
            str(selected_year) + " to " + end_month + " " + str(selected_year)
    elif selected_month + 2 == 13:
        start_month = calendar.month_name[selected_month]
        end_month = calendar.month_name[1]
        card_title = start_month + " " + \
            str(selected_year) + " to " + end_month + \
            " " + str(selected_year + 1)
    elif selected_month + 2 == 14:
        start_month = calendar.month_name[selected_month]
        end_month = calendar.month_name[2]
        card_title = start_month + " " + \
            str(selected_year) + " to " + end_month + \
            " " + str(selected_year + 1)
    return card_title


def search_month(start_month, end_month, selected_year, option):
    if option == "host":
        if end_month <= 12:
            query = models.Host.objects(
                month__gte=start_month,
                month__lte=end_month,
                year__in=[selected_year]
            )
            return query
        elif end_month == 13:
            query = models.Host.objects(
                (Q(month=11) & Q(year=selected_year)) | (Q(month=12) & Q(
                    year=selected_year)) | (Q(month=1) & Q(year=selected_year + 1))
            )
            return query
        elif end_month == 14:
            query = models.Host.objects(
                (Q(month=12) & Q(year=selected_year)) | (Q(month=1) & Q(
                    year=selected_year + 1)) | (Q(month=2) & Q(year=selected_year + 1))
            )
            return query

    elif option == "service":
        if end_month <= 12:
            query = models.Service.objects(
                month__gte=start_month,
                month__lte=end_month,
                year__in=[selected_year]
            )
            return query
        elif end_month == 13:
            query = models.Service.objects(
                (Q(month=11) & Q(year=selected_year)) | (Q(month=12) & Q(
                    year=selected_year)) | (Q(month=1) & Q(year=selected_year + 1))
            )
            return query
        elif end_month == 14:
            query = models.Service.objects(
                (Q(month=12) & Q(year=selected_year)) | (Q(month=1) & Q(
                    year=selected_year + 1)) | (Q(month=2) & Q(year=selected_year + 1))
            )
            return query

def search_service(start_month, end_month, selected_year, service_name):
    if end_month <= 12:
        query = models.Service.objects(
            name=service_name,
            month__gte=start_month,
            month__lte=end_month,
            year__in=[selected_year])
        return query
    if end_month == 13:
        query = models.Service.objects(
            (Q(name=service_name) & Q(month=11) & Q(year=selected_year)) | Q(name=service_name) & (
                Q(month=12) & Q(year=selected_year)) | Q(name=service_name) & (Q(month=1) & Q(year=selected_year + 1))
        )
        return query
    elif end_month == 14:
        query = models.Service.objects(
            (Q(name=service_name) & Q(month=12) & Q(year=selected_year)) | Q(name=service_name) & (Q(month=1) & Q(
                year=selected_year + 1)) | Q(name=service_name) & (Q(month=2) & Q(year=selected_year + 1))
        )
        return query

def search_host(start_month, end_month, selected_year, host_name):
    if end_month <= 12:
        query = models.Host.objects(
            name=host_name,
            month__gte=start_month,
            month__lte=end_month,
            year__in=[selected_year])
        return query
    if end_month == 13:
        query = models.Host.objects(
            (Q(name=host_name) & Q(month=11) & Q(year=selected_year)) | Q(name=host_name) & (
                Q(month=12) & Q(year=selected_year)) | Q(name=host_name) & (Q(month=1) & Q(year=selected_year + 1))
        )
        return query
    elif end_month == 14:
        query = models.Host.objects(
            (Q(name=host_name) & Q(month=12) & Q(year=selected_year)) | Q(name=host_name) & (Q(month=1) & Q(
                year=selected_year + 1)) | Q(name=host_name) & (Q(month=2) & Q(year=selected_year + 1))
        )
        return query


def search_host_day_data(matching_data, selected_month, selected_year):
    host_day_dict = []
    
    for data in matching_data:
        day = data.created_date.day
        month = data.created_date.month
        day = str(day) + "-" + str(month)
        
        if host_day_dict:
            for check_day in host_day_dict:
                day_exists = any(check_day["day"] ==
                                 day for check_day in host_day_dict)
                if day_exists:
                    if check_day["day"] == day:
                        
                        if data.minutes >= 1440 :
                            check_day["time"] = check_day["time"] + 1440
                        else :
                            check_day["time"] = check_day["time"] + data.minutes
                        check_day["count"] = check_day["count"] + 1
                        break

                else:
                    date = day
                    if data.minutes >= 1440 :
                        time = 1440
                    else :
                        time = data.minutes
                    count = 1
                    start_day = {"day": day, "time": time, "count": count}
                    host_day_dict.append(start_day)
                    break

        else:
            date = day
            if data.minutes >= 1440 :
                time = 1440
            else :
                time = data.minutes
            count = 1
            start_day = {"day": day, "time": time, "count": count}
            host_day_dict.append(start_day)

    if selected_month + 2 == 13 : #! Month 11 now year to Month 1 next year
        
        #! First month
        query = models.Host.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_host = len(matching_data)

        for data in host_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                data["count"] = total_all_host - data["count"]
            else :
                break

        #! Second month
        query = models.Host.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        total_all_host = len(matching_data)
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_host - data["count"]
                elif int(month) == 1:
                    break

        #! Third month
        query = models.Host.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        total_all_host = len(matching_data)
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_host - data["count"]

    if selected_month + 2 == 14 : #! Month 12 now year to Month 2 next year

        #! First month
        query = models.Host.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_host = len(matching_data)
        
        for data in host_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                data["count"] = total_all_host - data["count"]
            else :
                break

        #! Second month
        query = models.Host.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        total_all_host = len(matching_data)
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_host - data["count"]
                elif int(month) == 2 :
                    break

        #! Third month
        query = models.Host.objects(
                                month=2, year=selected_year + 1)
        matching_data = query.all()
        total_all_host = len(matching_data)
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_host - data["count"]
    
    else :

        #! First month
        query = models.Host.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_host = len(matching_data)

        for data in host_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                data["count"] = total_all_host - data["count"]
            else :
                break
        
        #! Second month
        query = models.Host.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        total_all_host = len(matching_data)
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_host - data["count"]
                elif int(month) == selected_month + 2 :
                    break
        
        #! Third month
        query = models.Host.objects(
                                month=selected_month + 2, year=selected_year)
        matching_data = query.all()
        total_all_host = len(matching_data)
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_host - data["count"]
    
    
    return host_day_dict

def search_service_day_data(matching_data, selected_month, selected_year):
    service_day_dict = []
    
    for data in matching_data:
        day = data.created_date.day
        month = data.created_date.month
        day = str(day) + "-" + str(month)
        
        if service_day_dict:
            for check_day in service_day_dict:
                day_exists = any(check_day["day"] ==
                                 day for check_day in service_day_dict)
                if day_exists:
                    if check_day["day"] == day:
                        
                        if data.minutes >= 1440 :
                            check_day["time"] = check_day["time"] + 1440
                        else :
                            check_day["time"] = check_day["time"] + data.minutes
                        check_day["count"] = check_day["count"] + 1
                        break

                else:
                    date = day
                    if data.minutes >= 1440 :
                        time = 1440
                    else :
                        time = data.minutes
                    count = 1
                    start_day = {"day": day, "time": time, "count": count}
                    service_day_dict.append(start_day)
                    break

        else:
            date = day
            if data.minutes >= 1440 :
                time = 1440
            else :
                time = data.minutes
            count = 1
            start_day = {"day": day, "time": time, "count": count}
            service_day_dict.append(start_day)

    if selected_month + 2 == 13 : #! Month 11 now year to Month 1 next year
        
        #! First month
        query = models.Service.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)

        for data in service_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                data["count"] = total_all_service - data["count"]
            else :
                break

        #! Second month
        query = models.Service.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_service - data["count"]
                elif int(month) == 1:
                    break

        #! Third month
        query = models.Service.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_service - data["count"]

    if selected_month + 2 == 14 : #! Month 12 now year to Month 2 next year

        #! First month
        query = models.Service.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)
        
        for data in service_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                data["count"] = total_all_service - data["count"]
            else :
                break

        #! Second month
        query = models.Service.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_service - data["count"]
                elif int(month) == 2 :
                    break

        #! Third month
        query = models.Service.objects(
                                month=2, year=selected_year + 1)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_service - data["count"]
    
    else :

        #! First month
        query = models.Service.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)

        for data in service_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                data["count"] = total_all_service - data["count"]
            else :
                break
        
        #! Second month
        query = models.Service.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_service - data["count"]
                elif int(month) == selected_month + 2 :
                    break
        
        #! Third month
        query = models.Service.objects(
                                month=selected_month + 2, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    data["count"] = total_all_service - data["count"]
    
    
    return service_day_dict

def get_day_in_month(month, year):
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if 1 <= month <= 12:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            days_in_month[1] = 29
        num_days = days_in_month[month - 1]

    return num_days


def get_all_quarter_data(month, year):
    quarter_month = {}
    many_month = 3
    current_date = datetime.datetime.now()
    month_now = int(current_date.strftime("%m"))
    day_now = int(current_date.strftime("%d"))

    for i in range(1, 4):
        if i == 1:
            num_days = get_day_in_month(month, year)

            if month == month_now:
                first_month = {str(i)+"-"+str(month): {"date": str(i)+"-" +
                                                       str(month), 'sla': 100} for i in range(1, day_now + 1)}
                many_month = 1
                break
            else:
                first_month = {str(i)+"-"+str(month): {"date": str(i)+"-" +
                                                       str(month), 'sla': 100} for i in range(1, num_days + 1)}

        elif i == 2:
            if month + 1 == 13:
                num_days = get_day_in_month(1, year + 1)
                if 1 == month_now:
                    second_month = {str(i)+"-"+str(1): {"date": str(i)+"-" +
                                                        str(1), 'sla': 100} for i in range(1, day_now + 1)}
                    many_month = 2
                    break
                else:
                    second_month = {str(i)+"-"+str(1): {"date": str(i)+"-" +
                                                        str(1), 'sla': 100} for i in range(1, num_days + 1)}
            else:
                num_days = get_day_in_month(month + 1, year)
                if month + 1 == month_now:
                    second_month = {str(i)+"-"+str(month + 1): {"date": str(i)+"-" +
                                                                str(month + 1), 'sla': 100} for i in range(1, day_now + 1)}
                    many_month = 2
                    break
                else:
                    second_month = {str(i)+"-"+str(month + 1): {"date": str(i)+"-" +
                                                                str(month + 1), 'sla': 100} for i in range(1, num_days + 1)}

        elif i == 3:
            if month + 2 == 13:
                num_days = get_day_in_month(1, year + 1)
                if 1 == month_now:
                    third_month = {str(i)+"-"+str(1): {"date": str(i)+"-" +
                                                       str(1), 'sla': 100} for i in range(1, day_now + 1)}

                    break
                else:
                    third_month = {str(i)+"-"+str(1): {"date": str(i)+"-" +
                                                       str(1), 'sla': 100} for i in range(1, num_days + 1)}
            elif month + 2 == 14:
                num_days = get_day_in_month(2, year + 1)
                if 2 == month_now:
                    third_month = {str(i)+"-"+str(2): {"date": str(i)+"-" +
                                                       str(2), 'sla': 100} for i in range(1, day_now + 1)}
                    break
                else:
                    third_month = {str(i)+"-"+str(2): {"date": str(i)+"-" +
                                                       str(2), 'sla': 100} for i in range(1, num_days + 1)}
            else:
                num_days = get_day_in_month(month + 2, year)
                if month + 2 == month_now:
                    third_month = {str(i)+"-"+str(month + 2): {"date": str(i)+"-" +
                                                               str(month + 2), 'sla': 100} for i in range(1, day_now + 1)}
                    break
                else:
                    third_month = {str(i)+"-"+str(month + 2): {"date": str(i)+"-" +
                                                               str(month + 2), 'sla': 100} for i in range(1, num_days + 1)}
    if many_month == 1:
        quarter_month = first_month
    elif many_month == 2:
        quarter_month = {**first_month, **second_month}
    else:
        quarter_month = {**first_month, **second_month, **
                         third_month}
    return quarter_month


def get_day_data(selected_month, selected_year, option):
    start_month = selected_month
    end_month = selected_month + 2
    if option == "host":
        if end_month > 12:
            query = search_month(start_month, end_month, selected_year, "host")
        else:
            query = search_month(start_month, end_month, selected_year, "host")

        host = query.all()
        
        host_list_id = []
        if host:
            for hosts in host:
                for value in hosts.host_list:
                    if value.last_state != -1:
                        host_list_id.append(value.id)

            query = models.HostList.objects(id__in=host_list_id)
            matching_data = query.all()
            host_day_dict = search_host_day_data(matching_data, selected_month, selected_year)
            quarter_month_dict = get_all_quarter_data(
                selected_month, selected_year)

            data_dict = {item['day']: {"date": item['day'], 'sla': round(
                (1440 - (item['time']/item['count']))/1440 * 100, 2)} for item in host_day_dict}

    elif option == "service":
        if end_month > 12:
            query = search_month(start_month, end_month, selected_year, "service")
        else:
            query = search_month(start_month, end_month, selected_year, "service")

        service = query.all()
        
        service_list_id = []
        if service:
            for services in service:
                for value in services.service_list:
                    if value.last_state != -1:
                        service_list_id.append(value.id)

            query = models.ServiceList.objects(id__in=service_list_id)
            matching_data = query.all()
            service_day_dict = search_service_day_data(matching_data, selected_month, selected_year)
            quarter_month_dict = get_all_quarter_data(
                selected_month, selected_year)

            data_dict = {item['day']: {"date": item['day'], 'sla': round(
                (1440 - (item['time']/item['count']))/1440 * 100, 2)} for item in service_day_dict}

    for key in quarter_month_dict:
        if key in data_dict:
            quarter_month_dict[key]['sla'] = data_dict[key]['sla']

    return quarter_month_dict


def get_host_quarter_data(selected_month, selected_year):

    start_month = selected_month
    end_month = selected_month + 2
    avg_sla = 0
    count = 0
    host_all_count = 0
    host_name = []
    host_sla = []
    host_sla_first_month = []
    host_sla_second_month = []
    host_sla_third_month = []
    host_sla_sum_first_month = 0
    host_sla_sum_second_month = 0
    host_sla_sum_third_month = 0
    host_ip = []
    host_count = []
    host_count_first_month = []
    host_count_second_month = []
    host_count_third_month = []
    host_count_sum_first_month = 0
    host_count_sum_second_month = 0
    host_count_sum_third_month = 0
    

    if end_month > 12:
        query = search_month(start_month, end_month, selected_year, "host")
        matching_hosts = query.all()
        for host in matching_hosts:
            avg_sla += host.availability
            host_all_count += host.count
            count += 1
            if host.name in host_name:
                continue
            else:
                host_name.append(host.name)
        for host in host_name:
            query = search_host(start_month, end_month, selected_year, host)
            matching_hosts = query.all()
            sla = 0
            count_down = 0
            month_count = 1

            for host in matching_hosts:
                sla += host.availability
                count_down += host.count
                if month_count == 1 :
                    host_count_first_month.append(host.count)
                    host_sla_first_month.append(host.availability)
                    month_count += 1
                elif month_count == 2 :
                    host_count_second_month.append(host.count)
                    host_sla_second_month.append(host.availability)
                    month_count += 1
                else :
                    host_count_third_month.append(host.count)
                    host_sla_third_month.append(host.availability)
                if host.ip_address in host_ip:
                    # continue
                    host_ip.append(host.ip_address)
                else:
                    host_ip.append(host.ip_address)
            sla = sla / len(matching_hosts)
            host_sla.append(sla)
            host_count.append(count_down)

    else:
        
        query = search_month(start_month, end_month, selected_year, "host")
        matching_hosts = query.all()
        for host in matching_hosts:
            avg_sla += host.availability
            host_all_count += host.count
            count += 1
            if host.name in host_name:
                continue
            else:
                host_name.append(host.name)

        for host in host_name:
            
            query = search_host(start_month, end_month, selected_year, host)
            matching_hosts = query.all()
            sla = 0
            count_down = 0
            month_count = 1
            for host in matching_hosts:
                sla += host.availability
                count_down += host.count
                if month_count == 1 :
                    host_count_first_month.append(host.count)
                    host_sla_first_month.append(host.availability)
                    month_count += 1
                elif month_count == 2 :
                    host_count_second_month.append(host.count)
                    host_sla_second_month.append(host.availability)
                    month_count += 1
                else :
                    host_count_third_month.append(host.count)
                    host_sla_third_month.append(host.availability)
        
                if host.ip_address in host_ip:
                    # continue
                    host_ip.append(host.ip_address)
                else:
                    host_ip.append(host.ip_address)
            
            sla = sla / len(matching_hosts)
            host_sla.append(sla)
            host_count.append(count_down)

    #! sum SLA and Host count down per down
    host_count_sum_first_month = sum(host_count_first_month)
    host_count_sum_second_month = sum(host_count_second_month)
    host_count_sum_third_month = sum(host_count_third_month)
    
    if len(host_sla_first_month) > 0:
        host_sla_sum_first_month = sum(host_sla_first_month) / len(host_sla_first_month)
    else :
        host_sla_sum_first_month = 100

    if len(host_sla_second_month) > 0:
        host_sla_sum_second_month = sum(host_sla_second_month) / len(host_sla_second_month)
    else :
        host_sla_sum_second_month = 100
        
    if len(host_sla_third_month) > 0:
        host_sla_sum_third_month = sum(host_sla_third_month) / len(host_sla_third_month)
    else :
        host_sla_sum_third_month = 100



    if avg_sla != 0:
        avg_sla = avg_sla / count
    card_title = get_name_month(selected_month, selected_year)
    # print(host_name)    
    # print("\n" , host_count)
    # return avg_sla, host_all_count, host_name, host_sla, host_ip, host_count, card_title, host_sla_first_month, host_sla_second_month, 
    return (
        avg_sla,
        host_all_count,
        host_name, host_sla,
        host_ip, host_count,
        card_title,
        host_sla_first_month,
        host_sla_second_month,
        host_sla_third_month,
        host_count_first_month,
        host_count_second_month,
        host_count_third_month,
        host_count_sum_first_month,
        host_count_sum_second_month,
        host_count_sum_third_month,
        host_sla_sum_first_month,
        host_sla_sum_second_month,
        host_sla_sum_third_month
    )

def get_service_quarter_data(selected_month, selected_year):

    start_month = selected_month
    end_month = selected_month + 2
    avg_sla = 0
    count = 0
    service_all_count = 0
    service_name = []
    service_sla = []
    service_sla_first_month = []
    service_sla_second_month = []
    service_sla_third_month = []
    service_sla_sum_first_month = 0
    service_sla_sum_second_month = 0
    service_sla_sum_third_month = 0
    service_count = []
    service_count_first_month = []
    service_count_second_month = []
    service_count_third_month = []
    service_count_sum_first_month = 0
    service_count_sum_second_month = 0
    service_count_sum_third_month = 0
    

    if end_month > 12:
        query = search_month(start_month, end_month, selected_year, "service")
        matching_services = query.all()
        for service in matching_services:
            avg_sla += service.availability
            service_all_count += service.count
            count += 1
            if service.name in service_name:
                continue
            else:
                service_name.append(service.name)
        for service in service_name:
            query = search_service(start_month, end_month, selected_year, service)
            matching_services = query.all()
            sla = 0
            count_down = 0
            month_count = 1

            for service in matching_services:
                sla += service.availability
                count_down += service.count
                if month_count == 1 :
                    service_count_first_month.append(service.count)
                    service_sla_first_month.append(service.availability)
                    month_count += 1
                elif month_count == 2 :
                    service_count_second_month.append(service.count)
                    service_sla_second_month.append(service.availability)
                    month_count += 1
                else :
                    service_count_third_month.append(service.count)
                    service_sla_third_month.append(service.availability)
            sla = sla / len(matching_services)
            service_sla.append(sla)
            service_count.append(count_down)

    else:
        query = search_month(start_month, end_month, selected_year, "service")
        matching_services = query.all()
        for service in matching_services:
            avg_sla += service.availability
            service_all_count += service.count
            count += 1
            if service.name in service_name:
                continue
            else:
                service_name.append(service.name)

        for service in service_name:
            query = search_service(start_month, end_month, selected_year, service)
            matching_services = query.all()
            sla = 0
            count_down = 0
            month_count = 1
            for service in matching_services:
                sla += service.availability
                count_down += service.count
                if month_count == 1 :
                    service_count_first_month.append(service.count)
                    service_sla_first_month.append(service.availability)
                    month_count += 1
                elif month_count == 2 :
                    service_count_second_month.append(service.count)
                    service_sla_second_month.append(service.availability)
                    month_count += 1
                else :
                    service_count_third_month.append(service.count)
                    service_sla_third_month.append(service.availability)
            
            sla = sla / len(matching_services)
            service_sla.append(sla)
            service_count.append(count_down)

    #! sum SLA and service count down per down
    service_count_sum_first_month = sum(service_count_first_month)
    service_count_sum_second_month = sum(service_count_second_month)
    service_count_sum_third_month = sum(service_count_third_month)
    
    if len(service_sla_first_month) > 0:
        service_sla_sum_first_month = sum(service_sla_first_month) / len(service_sla_first_month)
    else :
        service_sla_sum_first_month = 100

    if len(service_sla_second_month) > 0:
        service_sla_sum_second_month = sum(service_sla_second_month) / len(service_sla_second_month)
    else :
        service_sla_sum_second_month = 100
        
    if len(service_sla_third_month) > 0:
        service_sla_sum_third_month = sum(service_sla_third_month) / len(service_sla_third_month)
    else :
        service_sla_sum_third_month = 100

    if avg_sla != 0:
        avg_sla = avg_sla / count
    card_title = get_name_month(selected_month, selected_year)
    return (
        avg_sla,
        service_all_count,
        service_name, service_sla,
        service_count,
        card_title,
        service_sla_first_month,
        service_sla_second_month,
        service_sla_third_month,
        service_count_first_month,
        service_count_second_month,
        service_count_third_month,
        service_count_sum_first_month,
        service_count_sum_second_month,
        service_count_sum_third_month,
        service_sla_sum_first_month,
        service_sla_sum_second_month,
        service_sla_sum_third_month
    )

def search_month_same_year (start_month, start_year, end_month):
        
        query = models.Host.objects(
            month__gte=start_month,
            month__lte=end_month,
            year__in=[start_year]
        )

        return query
    
def search_month_another_year (start_month, start_year, end_month, end_year):
        
        january = 1
        december = 12

        query = models.Host.objects(
            (Q(month__gte=start_month) & Q(month__lte=december) & Q(year__in=[start_year])) | 
            (Q(month__gte=january) & Q(month__lte=end_month) & Q(year__in=[end_year]))
        )
        
        return query

def get_host_down_select_time(start_month, start_year, end_month, end_year, select_time) :

    host_data_down_select = {}
    host_down_over = []
    host_list_id = []
    host_data_name = []
    host_data_minutes = []
    host_data_last_time_down = []
    host_data_last_time_up = []
    unique_count_host_data_name = 0 
    all_count_down = 0

    if start_year == end_year :
        query = search_month_same_year (start_month, start_year, end_month)
        host = query.all()

        if host :
            for hosts in host:
                for value in hosts.host_list:
                    if value.last_state == 0:

                        if select_time >= 15 and  select_time < 60 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_list_id.append(value.id)
                                host_data_name.append(hosts.host_id)    

                        elif select_time == 60 :
                            if value.minutes >= select_time and value.minutes < 180 :
                                host_list_id.append(value.id)
                                host_data_name.append(hosts.host_id)

                        elif select_time >= 180 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_list_id.append(value.id)
                                host_data_name.append(hosts.host_id)      

                    

            query = models.HostList.objects(id__in=host_list_id)
            for host_data in query :
                host_data_minutes.append(host_data.minutes)
                host_data_last_time_down.append(host_data.last_time_down)
                host_data_last_time_up.append(host_data.last_time_up)
            
            
            host_data_down_select = {i: {"host_name": host_data_name[i], "host_minutes": host_data_minutes[i],
                                "host_last_time_down": host_data_last_time_down[i], "host_last_time_up": host_data_last_time_up[i]} for i in range(len(host_data_name))}
            
            unique_host_data_name = set(host_data_name)
            unique_count_host_data_name = len(unique_host_data_name)
            all_count_down = len(host_data_name)

    else :
        query = search_month_another_year (start_month, start_year, end_month, end_year)
        host = query.all()

        if host :
            for hosts in host:
                for value in hosts.host_list:
                    if value.last_state == 0:

                        if select_time >= 15 and  select_time < 60 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_list_id.append(value.id)
                                host_data_name.append(hosts.host_id)    

                        elif select_time == 60 :
                            if value.minutes >= select_time and value.minutes < 180 :
                                host_list_id.append(value.id)
                                host_data_name.append(hosts.host_id)

                        elif select_time >= 180 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_list_id.append(value.id)
                                host_data_name.append(hosts.host_id)    
                    

            query = models.HostList.objects(id__in=host_list_id)
            for host_data in query :
                host_data_minutes.append(host_data.minutes)
                host_data_last_time_down.append(host_data.last_time_down)
                host_data_last_time_up.append(host_data.last_time_up)
            
            
            host_data_down_select = {i: {"host_name": host_data_name[i], "host_minutes": host_data_minutes[i],
                                "host_last_time_down": host_data_last_time_down[i], "host_last_time_up": host_data_last_time_up[i]} for i in range(len(host_data_name))}
            
            unique_host_data_name = set(host_data_name)
            unique_count_host_data_name = len(unique_host_data_name)
            all_count_down = len(host_data_name)


    return (
            host_data_down_select,
            unique_count_host_data_name,
            all_count_down
    )   

DORM_LIST = [
    "Dorm10", 
    "Dorm11",
    "Dorm12",
    "Dorm13",
    "Dorm14",
    "Dorm15",
]


@caches.cache.cached(timeout=10800, key_prefix='get_ap_list_with_sla')
def get_ap_list_with_sla(ap_prop):
    get_ap_list = ap_prop
    if get_ap_list is None:
        get_ap_list = []
    ap_list = []
    location_data = []
    for location in location_list():
        location_data.append({
            "location_id": location.location_id,
            "lat": location.lat,
            "lng": location.lng,
        })
    for data in get_ap_list:
        for item in data["extensions"]["services_with_info"]:
            if item[0].startswith("AP"):
                name = item[0].split()[1]
                state = int(item[1])
                accessPoint_id = data["id"] + ":" + item[0]
                found_location = False
                default_lat = 7.0088136
                default_lng = 100.498062
                group_data = None
                for location in location_data:
                    if item[3] and "Group" in item[3]:
                        group_data = item[3].split(", ")[1].split(": ")[1]
                        if group_data == "Dorm10" and location["location_id"] == "DRM10":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"],
                                "availability": get_accessPoint_daily_sla(accessPoint_id)
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm11" and location["location_id"] == "DRM11":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"],
                                "availability": get_accessPoint_daily_sla(accessPoint_id)
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm12" and location["location_id"] == "DRM12":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"],
                                "availability": get_accessPoint_daily_sla(accessPoint_id)
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm13" and location["location_id"] == "DRM13":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"],
                                "availability": get_accessPoint_daily_sla(accessPoint_id)
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm14" and location["location_id"] == "DRM14":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"],
                                "availability": get_accessPoint_daily_sla(accessPoint_id)
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm15" and location["location_id"] == "DRM15":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"],
                                "availability": get_accessPoint_daily_sla(accessPoint_id)
                            })
                            found_location = True
                            break
                        elif name.startswith(location["location_id"]) and group_data not in DORM_LIST:
                                ap_list.append({
                                    "accessPoint_id": accessPoint_id,
                                    "name": name,
                                    "state": state,
                                    "lat": location["lat"],
                                    "lng": location["lng"],
                                    "group": location["location_id"],
                                    "availability": get_accessPoint_daily_sla(accessPoint_id)
                                })
                                found_location = True
                                break
                        
                    if data["id"] == "WLC" and name.startswith(location["location_id"]) and not name.startswith("DRM15") and not location["location_id"].startswith("DRM15"):
                        ap_list.append({
                            "accessPoint_id": accessPoint_id,
                            "name": name,
                            "state": state,
                            "lat": location["lat"],
                            "lng": location["lng"],
                            "group": location["location_id"],
                            "availability": get_accessPoint_daily_sla(accessPoint_id)
                        })
                        found_location = True
                        break
                    elif data["id"] == "WLC" and name.startswith("DRM15") and location["location_id"].startswith("DRM15"):
                        ap_list.append({
                            "accessPoint_id": accessPoint_id,
                            "name": name,
                            "state": state,
                            "lat": location["lat"],
                            "lng": location["lng"],
                            "group": "DRM15",
                            "availability": get_accessPoint_daily_sla(accessPoint_id)
                        })
                        found_location = True
                        break
                if not found_location :
                    ap_list.append({
                        "accessPoint_id": accessPoint_id,
                        "name": name,
                        "state": state,
                        "lat": default_lat,
                        "lng": default_lng,
                        "group": "",
                        "availability": get_accessPoint_daily_sla(accessPoint_id)
                    })
    return ap_list


def get_all_ap_list(ap_prop):
    get_ap_list = ap_prop
    if get_ap_list is None:
        get_ap_list = []
    ap_list = []
    location_data = []
    for location in location_list():
        location_data.append({
            "location_id": location.location_id,
            "lat": location.lat,
            "lng": location.lng,
        })
    for data in get_ap_list:
        for item in data["extensions"]["services_with_info"]:
            if item[0].startswith("AP"):
                name = item[0].split()[1]
                state = int(item[1])
                accessPoint_id = data["id"] + ":" + item[0]
                found_location = False
                default_lat = 7.0088136
                default_lng = 100.498062
                group_data = None
                for location in location_data:
                    if item[3] and "Group" in item[3]:
                        group_data = item[3].split(", ")[1].split(": ")[1]
                        if group_data == "Dorm10" and location["location_id"] == "DRM10":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm11" and location["location_id"] == "DRM11":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm12" and location["location_id"] == "DRM12":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm13" and location["location_id"] == "DRM13":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm14" and location["location_id"] == "DRM14":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm15" and location["location_id"] == "DRM15":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": location["lat"],
                                "lng": location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif name.startswith(location["location_id"]) and group_data not in DORM_LIST:
                                ap_list.append({
                                    "accessPoint_id": accessPoint_id,
                                    "name": name,
                                    "state": state,
                                    "lat": location["lat"],
                                    "lng": location["lng"],
                                    "group": location["location_id"]
                                })
                                found_location = True
                                break
                        
                    if data["id"] == "WLC" and name.startswith(location["location_id"]) and not name.startswith("DRM15") and not location["location_id"].startswith("DRM15"):
                        ap_list.append({
                            "accessPoint_id": accessPoint_id,
                            "name": name,
                            "state": state,
                            "lat": location["lat"],
                            "lng": location["lng"],
                            "group": location["location_id"]
                        })
                        found_location = True
                        break
                    elif data["id"] == "WLC" and name.startswith("DRM15") and location["location_id"].startswith("DRM15"):
                        ap_list.append({
                            "accessPoint_id": accessPoint_id,
                            "name": name,
                            "state": state,
                            "lat": location["lat"],
                            "lng": location["lng"],
                            "group": "DRM15"
                        })
                        found_location = True
                        break
                if not found_location :
                    ap_list.append({
                        "accessPoint_id": accessPoint_id,
                        "name": name,
                        "state": state,
                        "lat": default_lat,
                        "lng": default_lng,
                        "group": ""
                    })
    return ap_list


def get_host_daily_sla(host_id) :
    host_list_ids = []
    minutes = 0
    current_datetime = datetime.datetime.now()

    host = models.Host.objects(
        host_id=host_id, month=current_datetime.month, year=current_datetime.year).first()
    if host:
        if host.host_list and host.host_list is not None and host.host_list != [] :
            for value in host.host_list:
                host_list_ids.append(value.id)

            query = models.HostList.objects(
                id__in=host_list_ids)
            matching_data = query.all()

            for data in matching_data :

                timestamp = data.created_date
                try:
                    dt_object = datetime.datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    dt_object = datetime.datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S')
                day = dt_object.day

                if day == current_datetime.day :
                    minutes += data.minutes
            
            if minutes == 0 :
                return '{:.2f}'.format(round(100, 2))

            elif minutes >= 1440 :
                return 0
            
            else :
                sla = ((1440 - minutes) / 1440) * 100
                return '{:.4f}'.format(round(sla, 8))
        
        else :
            return '{:.2f}'.format(round(100, 2))
        

def get_service_daily_sla(service_id) :
    service_list_ids = []
    minutes = 0
    current_datetime = datetime.datetime.now()

    service = models.Service.objects(
        service_id=service_id, month=current_datetime.month, year=current_datetime.year).first()
    if service:

        if service.service_list and service.service_list is not None and service.service_list != [] :
            for value in service.service_list:
                service_list_ids.append(value.id)

            query = models.ServiceList.objects(
                id__in=service_list_ids)
            matching_data = query.all()

            for data in matching_data :

                timestamp = data.created_date

                try:
                    dt_object = datetime.datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    dt_object = datetime.datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S')

                day = dt_object.day

                if day == current_datetime.day :
                    minutes += data.minutes
            
            if minutes == 0 :
                return '{:.2f}'.format(round(100, 2))

            elif minutes >= 1440 :
                return 0
            
            else :
                sla = ((1440 - minutes) / 1440) * 100
                return '{:.4f}'.format(round(sla, 8))
        
        else :
            return '{:.2f}'.format(round(100, 2))
    

def get_accessPoint_daily_sla(accessPoint_id) :
    accessPoint_list_ids = []
    minutes = 0
    current_datetime = datetime.datetime.now()

    accessPoint = models.AccessPoint.objects(
        accessPoint_id=accessPoint_id, month=current_datetime.month, year=current_datetime.year).first()
    if accessPoint:

        if accessPoint.accessPoint_list and accessPoint.accessPoint_list is not None and accessPoint.accessPoint_list != [] :
            for value in accessPoint.accessPoint_list:
                accessPoint_list_ids.append(value.id)

            query = models.AccessPointList.objects(
                id__in=accessPoint_list_ids)
            matching_data = query.all()

            for data in matching_data :

                timestamp = data.created_date

                try:
                    dt_object = datetime.datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    dt_object = datetime.datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S')

                day = dt_object.day

                if day == current_datetime.day :
                    minutes += data.minutes
            
            if minutes == 0 :
                return '{:.2f}'.format(round(100, 2))

            elif minutes >= 1440 :
                return 0
            
            else :
                sla = ((1440 - minutes) / 1440) * 100
                return '{:.4f}'.format(round(sla, 8))
        
        else :
            return '{:.2f}'.format(round(100, 2))
    
    
def get_host_group_monthly_sla(group_id) :

    current_datetime = datetime.datetime.now()
    sla = 0
    count = 0

    query = models.Host.objects(
                                month=current_datetime.month, year=current_datetime.year)
    matching_data = query.all()
    

    for host in matching_data :
        group = host.groups
        
        for group_name in group :
            if group_name == group_id :
                sla += host.availability
                count += 1
                break
    
    if count > 0:
        return '{:.4f}'.format(round(sla / count, 8))
    else:
        return ""
    
    
def get_service_group_monthly_sla(group_id) :

    current_datetime = datetime.datetime.now()
    sla = 0
    count = 0

    query = models.Service.objects(
                                month=current_datetime.month, year=current_datetime.year)
    matching_data = query.all()
    

    for service in matching_data :
        group = service.groups
        
        for group_name in group :
            if group_name == group_id :
                sla += service.availability
                count += 1
                break
            
    if count > 0:
        return '{:.4f}'.format(round(sla / count, 8))
    else:
        return "" 