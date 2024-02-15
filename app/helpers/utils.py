from .. import models
from .. import caches
import datetime
import calendar
from mongoengine import Q


def sla_status_list():
    return {
        "ok_status": 99.982,
        "critical_status": 99.75
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

    elif option == "access_point":
        if end_month <= 12:
            query = models.AccessPoint.objects(
                month__gte=start_month,
                month__lte=end_month,
                year__in=[selected_year]
            )
            return query
        elif end_month == 13:
            query = models.AccessPoint.objects(
                (Q(month=11) & Q(year=selected_year)) | (Q(month=12) & Q(
                    year=selected_year)) | (Q(month=1) & Q(year=selected_year + 1))
            )
            return query
        elif end_month == 14:
            query = models.AccessPoint.objects(
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

def search_accessPoint(start_month, end_month, selected_year, accessPoint_name):
    if end_month <= 12:
        query = models.AccessPoint.objects(
            name=accessPoint_name,
            month__gte=start_month,
            month__lte=end_month,
            year__in=[selected_year])
        return query
    if end_month == 13:
        query = models.AccessPoint.objects(
            (Q(name=accessPoint_name) & Q(month=11) & Q(year=selected_year)) | Q(name=accessPoint_name) & (
                Q(month=12) & Q(year=selected_year)) | Q(name=accessPoint_name) & (Q(month=1) & Q(year=selected_year + 1))
        )
        return query
    elif end_month == 14:
        query = models.AccessPoint.objects(
            (Q(name=accessPoint_name) & Q(month=12) & Q(year=selected_year)) | Q(name=accessPoint_name) & (Q(month=1) & Q(
                year=selected_year + 1)) | Q(name=accessPoint_name) & (Q(month=2) & Q(year=selected_year + 1))
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
                        break

                else:
                    date = day
                    if data.minutes >= 1440 :
                        time = 1440
                    else :
                        time = data.minutes
                    count = 1
                    start_day = {"day": day, "time": time}
                    host_day_dict.append(start_day)
                    break

        else:
            date = day
            if data.minutes >= 1440 :
                time = 1440
            else :
                time = data.minutes
            count = 1
            start_day = {"day": day, "time": time}
            host_day_dict.append(start_day)

    if selected_month + 2 == 13 :
        
        query = models.Host.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        

        for data in host_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break

        query = models.Host.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == 1:
                    break

        query = models.Host.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')

    if selected_month + 2 == 14 :

        query = models.Host.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        
        
        for data in host_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break

        query = models.Host.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == 2 :
                    break

        query = models.Host.objects(
                                month=2, year=selected_year + 1)
        matching_data = query.all()
        
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
    
    else :

        query = models.Host.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        

        for data in host_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break
        
        query = models.Host.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == selected_month + 2 :
                    break
        
        query = models.Host.objects(
                                month=selected_month + 2, year=selected_year)
        matching_data = query.all()
        
        if len(matching_data) == 0 :
            for data in host_day_dict :
                day, month = data['day'].split('-')
    
    
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
                        
                        break

                else:
                    date = day
                    if data.minutes >= 1440 :
                        time = 1440
                    else :
                        time = data.minutes
                    count = 1
                    start_day = {"day": day, "time": time}
                    service_day_dict.append(start_day)
                    break

        else:
            date = day
            if data.minutes >= 1440 :
                time = 1440
            else :
                time = data.minutes
            count = 1
            start_day = {"day": day, "time": time}
            service_day_dict.append(start_day)

    if selected_month + 2 == 13 :
        
        query = models.Service.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)

        for data in service_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break

        query = models.Service.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == 1:
                    break

        query = models.Service.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                
                    

    if selected_month + 2 == 14 :

        query = models.Service.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)
        
        for data in service_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break

        query = models.Service.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == 2 :
                    break

        query = models.Service.objects(
                                month=2, year=selected_year + 1)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
    
    else :

        query = models.Service.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)

        for data in service_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break
        
        query = models.Service.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == selected_month + 2 :
                    break
        
        query = models.Service.objects(
                                month=selected_month + 2, year=selected_year)
        matching_data = query.all()
        total_all_service = len(matching_data)
        if len(matching_data) == 0 :
            for data in service_day_dict :
                day, month = data['day'].split('-')
    return service_day_dict


def search_accessPoint_day_data(matching_data, selected_month, selected_year):
    accessPoint_day_dict = []
    
    for data in matching_data:
        day = data.created_date.day
        month = data.created_date.month
        day = str(day) + "-" + str(month)
        
        if accessPoint_day_dict:
            for check_day in accessPoint_day_dict:
                day_exists = any(check_day["day"] ==
                                 day for check_day in accessPoint_day_dict)
                if day_exists:
                    if check_day["day"] == day:
                        
                        if data.minutes >= 1440 :
                            check_day["time"] = check_day["time"] + 1440
                        else :
                            check_day["time"] = check_day["time"] + data.minutes
                        
                        break

                else:
                    date = day
                    if data.minutes >= 1440 :
                        time = 1440
                    else :
                        time = data.minutes
                    count = 1
                    start_day = {"day": day, "time": time}
                    accessPoint_day_dict.append(start_day)
                    break

        else:
            date = day
            if data.minutes >= 1440 :
                time = 1440
            else :
                time = data.minutes
            count = 1
            start_day = {"day": day, "time": time}
            accessPoint_day_dict.append(start_day)

    if selected_month + 2 == 13 :
        
        query = models.AccessPoint.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)

        for data in accessPoint_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break

        query = models.AccessPoint.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)
        if len(matching_data) == 0 :
            for data in accessPoint_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == 1:
                    break

        query = models.AccessPoint.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)
        if len(matching_data) == 0 :
            for data in accessPoint_day_dict :
                day, month = data['day'].split('-')
                
    if selected_month + 2 == 14 :

        query = models.AccessPoint.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)
        
        for data in accessPoint_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break

        query = models.AccessPoint.objects(
                                month=1, year=selected_year + 1)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)
        if len(matching_data) == 0 :
            for data in accessPoint_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == 2 :
                    break

        query = models.AccessPoint.objects(
                                month=2, year=selected_year + 1)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)
        if len(matching_data) == 0 :
            for data in accessPoint_day_dict :
                day, month = data['day'].split('-')
    
    else :

        query = models.AccessPoint.objects(
                                month=selected_month, year=selected_year)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)

        for data in accessPoint_day_dict :
            day, month = data['day'].split('-')
            if int(month) == selected_month :
                continue
            else :
                break
        
        query = models.AccessPoint.objects(
                                month=selected_month + 1, year=selected_year)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)
        if len(matching_data) == 0 :
            for data in accessPoint_day_dict :
                day, month = data['day'].split('-')
                if int(month) == selected_month :
                    continue
                elif int(month) == selected_month + 2 :
                    break
        
        query = models.AccessPoint.objects(
                                month=selected_month + 2, year=selected_year)
        matching_data = query.all()
        total_all_accessPoint = len(matching_data)
        if len(matching_data) == 0 :
            for data in accessPoint_day_dict :
                day, month = data['day'].split('-')
    return accessPoint_day_dict


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
                    host_list_id.append(value.id)

            query = models.HostList.objects(id__in=host_list_id)
            matching_data = query.all()
            host_day_dict = search_host_day_data(matching_data, selected_month, selected_year)
            quarter_month_dict = get_all_quarter_data(
                selected_month, selected_year)
            
            query = models.Host.objects(
                                month=selected_month, year=selected_year)
            total_host = query.count()
            

            data_dict = {item['day']: {"date": item['day'], 'sla': '{:.4f}'.format(round(
                ((total_host * 1440 ) - (item['time']))/(1440 * total_host) * 100, 4))} for item in host_day_dict}
            
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
                    service_list_id.append(value.id)

            query = models.ServiceList.objects(id__in=service_list_id)
            matching_data = query.all()
            service_day_dict = search_service_day_data(matching_data, selected_month, selected_year)
            quarter_month_dict = get_all_quarter_data(
                selected_month, selected_year)

            query = models.Service.objects(
                                month=selected_month, year=selected_year)
            total_service = query.count()
            

            data_dict = {item['day']: {"date": item['day'], 'sla': '{:.4f}'.format(round(
                ((total_service * 1440 ) - (item['time']))/(1440 * total_service) * 100, 4))} for item in service_day_dict}

    elif option == "access_point":
        if end_month > 12:
            query = search_month(start_month, end_month, selected_year, "access_point")
        else:
            query = search_month(start_month, end_month, selected_year, "access_point")

        accessPoint = query.all()
        
        accessPoint_list_id = []
        if accessPoint:
            for accessPoints in accessPoint:
                for value in accessPoints.accessPoint_list:
                    accessPoint_list_id.append(value.id)

            query = models.AccessPointList.objects(id__in=accessPoint_list_id)
            matching_data = query.all()
            accessPoint_day_dict = search_accessPoint_day_data(matching_data, selected_month, selected_year)
            quarter_month_dict = get_all_quarter_data(
                selected_month, selected_year)

            query = models.AccessPoint.objects(
                                month=selected_month, year=selected_year)
            total_accessPoint = query.count()
            

            data_dict = {item['day']: {"date": item['day'], 'sla': '{:.4f}'.format(round(
                ((total_accessPoint * 1440 ) - (item['time']))/(1440 * total_accessPoint) * 100, 4))} for item in accessPoint_day_dict}

    for key in quarter_month_dict:
        if key in data_dict:
            quarter_month_dict[key]['sla'] = float(data_dict[key]['sla'])

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
    host_name_first_month = []
    host_name_second_month = []
    host_name_third_month = []
    

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
            january = 1
            december = 12

            first_month = start_month
            if first_month + 1 == 13 :
                second_month = january
            else :
                second_month = december

            

            for host in matching_hosts:
                sla += host.availability
                count_down += host.count

                if host.month ==  first_month :
                    host_name_first_month.append(host.host_id)
                    host_count_first_month.append(host.count)
                    host_sla_first_month.append(host.availability)
                    

                elif host.month == second_month :
                        host_name_second_month.append(host.host_id)
                        host_count_second_month.append(host.count)
                        host_sla_second_month.append(host.availability)
                        

                else :
                    host_name_third_month.append(host.host_id)
                    host_count_third_month.append(host.count)
                    host_sla_third_month.append(host.availability)

                if host.ip_address in host_ip:
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
            first_month = start_month
            second_month = first_month  +  1
            third_month = second_month + 1

            for host in matching_hosts:
                sla += host.availability
                count_down += host.count

                if host.month ==  first_month :
                    host_name_first_month.append(host.host_id)
                    host_count_first_month.append(host.count)
                    host_sla_first_month.append(host.availability)
                    

                elif host.month == second_month :
                        host_name_second_month.append(host.host_id)
                        host_count_second_month.append(host.count)
                        host_sla_second_month.append(host.availability)
                        

                else :
                    host_name_third_month.append(host.host_id)
                    host_count_third_month.append(host.count)
                    host_sla_third_month.append(host.availability)
        
                if host.ip_address in host_ip:
                    host_ip.append(host.ip_address)
                else:
                    host_ip.append(host.ip_address)
            
            sla = sla / len(matching_hosts)
            host_sla.append(sla)
            host_count.append(count_down)

    host_count_sum_first_month = sum(host_count_first_month)
    host_count_sum_second_month = sum(host_count_second_month)
    host_count_sum_third_month = sum(host_count_third_month)
    
    if len(host_sla_first_month) > 0:
        host_sla_sum_first_month = sum(host_sla_first_month) / len(host_sla_first_month)
        print("sum : " , sum(host_sla_first_month) , " count" , len(host_sla_first_month))
    else :
        host_sla_sum_first_month = 100

    if len(host_sla_second_month) > 0:
        host_sla_sum_second_month = sum(host_sla_second_month) / len(host_sla_second_month)
        print("sum : " , sum(host_sla_second_month) , " count" , len(host_sla_second_month))
    else :
        host_sla_sum_second_month = 100
        
    if len(host_sla_third_month) > 0:
        host_sla_sum_third_month = sum(host_sla_third_month) / len(host_sla_third_month)
    else :
        host_sla_sum_third_month = 100



    if avg_sla != 0:
        avg_sla = avg_sla / count
    card_title = get_name_month(selected_month, selected_year)

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
        host_sla_sum_third_month,
        host_name_first_month,
        host_name_second_month,
        host_name_third_month
    )

def get_accessPoint_quarter_data(selected_month, selected_year):

    start_month = selected_month
    end_month = selected_month + 2
    avg_sla = 0
    count = 0
    accessPoint_all_count = 0
    accessPoint_name = []
    accessPoint_sla = []
    accessPoint_sla_first_month = []
    accessPoint_sla_second_month = []
    accessPoint_sla_third_month = []
    accessPoint_sla_sum_first_month = 0
    accessPoint_sla_sum_second_month = 0
    accessPoint_sla_sum_third_month = 0
    accessPoint_ip = []
    accessPoint_count = []
    accessPoint_count_first_month = []
    accessPoint_count_second_month = []
    accessPoint_count_third_month = []
    accessPoint_count_sum_first_month = 0
    accessPoint_count_sum_second_month = 0
    accessPoint_count_sum_third_month = 0
    accessPoint_name_first_month = []
    accessPoint_name_second_month = []
    accessPoint_name_third_month = []
    

    if end_month > 12:
        query = search_month(start_month, end_month, selected_year, "access_point")
        matching_accessPoints = query.all()
        for accessPoint in matching_accessPoints:
            avg_sla += accessPoint.availability
            accessPoint_all_count += accessPoint.count
            count += 1
            if accessPoint.name in accessPoint_name:
                continue
            else:
                accessPoint_name.append(accessPoint.name)
        for accessPoint in accessPoint_name:
            query = search_accessPoint(start_month, end_month, selected_year, accessPoint)
            matching_accessPoints = query.all()
            sla = 0
            count_down = 0
            january = 1
            december = 12

            first_month = start_month
            if first_month + 1 == 13 :
                second_month = january
            else :
                second_month = december
            for accessPoint in matching_accessPoints:
                sla += accessPoint.availability
                count_down += accessPoint.count
                if accessPoint.month == first_month:
                    accessPoint_name_first_month.append(accessPoint.accessPoint_id)
                    accessPoint_count_first_month.append(accessPoint.count)
                    accessPoint_sla_first_month.append(accessPoint.availability)
                    
                elif accessPoint.month == second_month:
                    accessPoint_name_second_month.append(accessPoint.accessPoint_id)
                    accessPoint_count_second_month.append(accessPoint.count)
                    accessPoint_sla_second_month.append(accessPoint.availability)
                    
                else :
                    accessPoint_name_third_month.append(accessPoint.accessPoint_id)
                    accessPoint_count_third_month.append(accessPoint.count)
                    accessPoint_sla_third_month.append(accessPoint.availability)

            sla = sla / len(matching_accessPoints)
            accessPoint_sla.append(sla)
            accessPoint_count.append(count_down)

    else:
        query = search_month(start_month, end_month, selected_year, "access_point")
        matching_accessPoints = query.all()
        for accessPoint in matching_accessPoints:
            avg_sla += accessPoint.availability
            accessPoint_all_count += accessPoint.count
            count += 1
            if accessPoint.name in accessPoint_name:
                continue
            else:
                accessPoint_name.append(accessPoint.name)

        for accessPoint in accessPoint_name:
            
            query = search_accessPoint(start_month, end_month, selected_year, accessPoint)
            matching_accessPoints = query.all()
            sla = 0
            count_down = 0
            first_month = start_month
            second_month = first_month  +  1

            for accessPoint in matching_accessPoints:
                sla += accessPoint.availability
                count_down += accessPoint.count
                if accessPoint.month == first_month :
                    accessPoint_name_first_month.append(accessPoint.accessPoint_id)
                    accessPoint_count_first_month.append(accessPoint.count)
                    accessPoint_sla_first_month.append(accessPoint.availability)
                    
                elif accessPoint.month == second_month :
                        accessPoint_name_second_month.append(accessPoint.accessPoint_id)
                        accessPoint_count_second_month.append(accessPoint.count)
                        accessPoint_sla_second_month.append(accessPoint.availability)
                        
                else :
                    accessPoint_name_third_month.append(accessPoint.accessPoint_id)
                    accessPoint_count_third_month.append(accessPoint.count)
                    accessPoint_sla_third_month.append(accessPoint.availability)
            
            sla = sla / len(matching_accessPoints)
            accessPoint_sla.append(sla)
            accessPoint_count.append(count_down)

    accessPoint_count_sum_first_month = sum(accessPoint_count_first_month)
    accessPoint_count_sum_second_month = sum(accessPoint_count_second_month)
    accessPoint_count_sum_third_month = sum(accessPoint_count_third_month)
    
    if len(accessPoint_sla_first_month) > 0:
        accessPoint_sla_sum_first_month = sum(accessPoint_sla_first_month) / len(accessPoint_sla_first_month)
    else :
        accessPoint_sla_sum_first_month = 100

    if len(accessPoint_sla_second_month) > 0:
        accessPoint_sla_sum_second_month = sum(accessPoint_sla_second_month) / len(accessPoint_sla_second_month)
    else :
        accessPoint_sla_sum_second_month = 100
        
    if len(accessPoint_sla_third_month) > 0:
        accessPoint_sla_sum_third_month = sum(accessPoint_sla_third_month) / len(accessPoint_sla_third_month)
    else :
        accessPoint_sla_sum_third_month = 100



    if avg_sla != 0:
        avg_sla = avg_sla / count
    card_title = get_name_month(selected_month, selected_year)

    return (
        avg_sla,
        accessPoint_all_count,
        accessPoint_name, accessPoint_sla,
        accessPoint_count, card_title,
        accessPoint_sla_first_month,
        accessPoint_sla_second_month,
        accessPoint_sla_third_month,
        accessPoint_count_first_month,
        accessPoint_count_second_month,
        accessPoint_count_third_month,
        accessPoint_count_sum_first_month,
        accessPoint_count_sum_second_month,
        accessPoint_count_sum_third_month,
        accessPoint_sla_sum_first_month,
        accessPoint_sla_sum_second_month,
        accessPoint_sla_sum_third_month,
        accessPoint_name_first_month,
        accessPoint_name_second_month,
        accessPoint_name_third_month
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
    service_name_first_month = []
    service_name_second_month = []
    service_name_third_month = []
    

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
            january = 1
            december = 12

            first_month = start_month
            if first_month + 1 == 13 :
                second_month = january
            else :
                second_month = december

            for service in matching_services:
                sla += service.availability
                count_down += service.count

                if service.month == first_month :
                    service_name_first_month.append(service.service_id)
                    service_count_first_month.append(service.count)
                    service_sla_first_month.append(service.availability)
                    
                elif service.month == second_month:
                    service_name_second_month.append(service.service_id)
                    service_count_second_month.append(service.count)
                    service_sla_second_month.append(service.availability)
                    
                else :
                    service_name_third_month.append(service.service_id)
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
            first_month = start_month
            second_month = first_month  +  1

            for service in matching_services:
                sla += service.availability
                count_down += service.count

                if  service.month == first_month :
                    service_name_first_month.append(service.service_id)
                    service_count_first_month.append(service.count)
                    service_sla_first_month.append(service.availability)
            
                elif service.month == second_month :
                    service_name_second_month.append(service.service_id)
                    service_count_second_month.append(service.count)
                    service_sla_second_month.append(service.availability)
                    
                else :
                    service_name_third_month.append(service.service_id)
                    service_count_third_month.append(service.count)
                    service_sla_third_month.append(service.availability)
            
            sla = sla / len(matching_services)
            service_sla.append(sla)
            service_count.append(count_down)

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
        service_sla_sum_third_month,
        service_name_first_month,
        service_name_second_month,
        service_name_third_month
    )

def search_month_same_year (type,start_month, start_year, end_month):
        
        if type == "host" :
            query = models.Host.objects(
                month__gte=start_month,
                month__lte=end_month,
                year__in=[start_year]
            )

            return query
        
        else :
            query = models.AccessPoint.objects(
                month__gte=start_month,
                month__lte=end_month,
                year__in=[start_year]
            )

            return query
    
def search_month_another_year (type,start_month, start_year, end_month, end_year):
        
        january = 1
        december = 12
        
        if type == "host" :
            query = models.Host.objects(
                (Q(month__gte=start_month) & Q(month__lte=december) & Q(year__in=[start_year])) | 
                (Q(month__gte=january) & Q(month__lte=end_month) & Q(year__in=[end_year]))
            )
            
            return query
        else :
            query = models.AccessPoint.objects(
                (Q(month__gte=start_month) & Q(month__lte=december) & Q(year__in=[start_year])) | 
                (Q(month__gte=january) & Q(month__lte=end_month) & Q(year__in=[end_year]))
            )
            
            return query

def get_host_down_select_time(start_month, start_year, end_month, end_year, select_time) :
    print("host")
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
        query = search_month_same_year ("host",start_month, start_year, end_month)
        host = query.all()

        if host :
            for hosts in host:
                for value in hosts.host_list:
                    if value.last_state == 0:

                        if select_time >= 15 and  select_time < 60 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_data_name.append(hosts.name)   
                                host_data_minutes.append(value.minutes)
                                host_data_last_time_down.append(value.created_date)
                                host_data_last_time_up.append(value.updated_date)
    

                        elif select_time == 60 :
                            if value.minutes >= select_time and value.minutes < 180 :
                                host_data_name.append(hosts.name)   
                                host_data_minutes.append(value.minutes)
                                host_data_last_time_down.append(value.created_date)
                                host_data_last_time_up.append(value.updated_date)


                        elif select_time >= 180 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_data_name.append(hosts.name)   
                                host_data_minutes.append(value.minutes)
                                host_data_last_time_down.append(value.created_date)
                                host_data_last_time_up.append(value.updated_date)

                                

                    elif value.last_state == -2:
                        if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_data_name.append(hosts.name)   
                                host_data_minutes.append(value.minutes)
                                host_data_last_time_down.append(value.created_date)
                                host_data_last_time_up.append(value.updated_date)

                                
            host_data_down_select = {i: {"host_name": host_data_name[i], "host_minutes": host_data_minutes[i],
                                "host_last_time_down": host_data_last_time_down[i], "host_last_time_up": host_data_last_time_up[i]} for i in range(len(host_data_name))}
            
            unique_host_data_name = set(host_data_name)
            unique_count_host_data_name = len(unique_host_data_name)
            all_count_down = len(host_data_name)

    else :
        query = search_month_another_year ("host",start_month, start_year, end_month, end_year)
        host = query.all()

        if host :
            for hosts in host:
                for value in hosts.host_list:
                    if value.last_state == 0:

                        if select_time >= 15 and  select_time < 60 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_data_name.append(hosts.name)   
                                host_data_minutes.append(value.minutes)
                                host_data_last_time_down.append(value.created_date)
                                host_data_last_time_up.append(value.updated_date)
    

                        elif select_time == 60 :
                            if value.minutes >= select_time and value.minutes < 180 :
                                host_data_name.append(hosts.name)   
                                host_data_minutes.append(value.minutes)
                                host_data_last_time_down.append(value.created_date)
                                host_data_last_time_up.append(value.updated_date)


                        elif select_time >= 180 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_data_name.append(hosts.name)   
                                host_data_minutes.append(value.minutes)
                                host_data_last_time_down.append(value.created_date)
                                host_data_last_time_up.append(value.updated_date)


                    elif value.last_state == -2:
                        if value.minutes >= select_time and value.minutes < select_time * 2 :
                                host_data_name.append(hosts.name)   
                                host_data_minutes.append(value.minutes)
                                host_data_last_time_down.append(value.created_date)
                                host_data_last_time_up.append(value.updated_date)

            
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

def get_accessPoint_down_select_time(start_month, start_year, end_month, end_year, select_time) :
    print("AP")
    accessPoint_data_down_select = {}
    accessPoint_down_over = []
    accessPoint_list_id = []
    accessPoint_data_name = []
    accessPoint_data_minutes = []
    accessPoint_data_last_time_down = []
    accessPoint_data_last_time_up = []
    unique_count_accessPoint_data_name = 0 
    all_count_down = 0

    if start_year == end_year :
        query = search_month_same_year ("accesspoint",start_month, start_year, end_month)
        accessPoint = query.all()

        if accessPoint :
            for accessPoints in accessPoint:
                for value in accessPoints.accessPoint_list:
                    if value.last_state == 0:

                        if select_time >= 15 and  select_time < 60 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                accessPoint_data_name.append(accessPoints.name)   
                                accessPoint_data_minutes.append(value.minutes)
                                accessPoint_data_last_time_down.append(value.created_date)
                                accessPoint_data_last_time_up.append(value.updated_date)
    

                        elif select_time == 60 :
                            if value.minutes >= select_time and value.minutes < 180 :
                                accessPoint_data_name.append(accessPoints.name)   
                                accessPoint_data_minutes.append(value.minutes)
                                accessPoint_data_last_time_down.append(value.created_date)
                                accessPoint_data_last_time_up.append(value.updated_date)


                        elif select_time >= 180 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                accessPoint_data_name.append(accessPoints.name)   
                                accessPoint_data_minutes.append(value.minutes)
                                accessPoint_data_last_time_down.append(value.created_date)
                                accessPoint_data_last_time_up.append(value.updated_date)

                                

                    elif value.last_state == -2:
                        if value.minutes >= select_time and value.minutes < select_time * 2 :
                                accessPoint_data_name.append(accessPoints.name)   
                                accessPoint_data_minutes.append(value.minutes)
                                accessPoint_data_last_time_down.append(value.created_date)
                                accessPoint_data_last_time_up.append(value.updated_date)

                                
            accessPoint_data_down_select = {i: {"accessPoint_name": accessPoint_data_name[i], "accessPoint_minutes": accessPoint_data_minutes[i],
                                "accessPoint_last_time_down": accessPoint_data_last_time_down[i], "accessPoint_last_time_up": accessPoint_data_last_time_up[i]} for i in range(len(accessPoint_data_name))}
            
            
            unique_accessPoint_data_name = set(accessPoint_data_name)
            unique_count_accessPoint_data_name = len(unique_accessPoint_data_name)
            all_count_down = len(accessPoint_data_name)

    else :
        query = search_month_another_year ("accesspoint",start_month, start_year, end_month, end_year)
        accessPoint = query.all()

        if accessPoint :
            for accessPoints in accessPoint:
                for value in accessPoints.accessPoint_list:
                    if value.last_state == 0:

                        if select_time >= 15 and  select_time < 60 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                accessPoint_data_name.append(accessPoints.name)   
                                accessPoint_data_minutes.append(value.minutes)
                                accessPoint_data_last_time_down.append(value.created_date)
                                accessPoint_data_last_time_up.append(value.updated_date)
    

                        elif select_time == 60 :
                            if value.minutes >= select_time and value.minutes < 180 :
                                accessPoint_data_name.append(accessPoints.name)   
                                accessPoint_data_minutes.append(value.minutes)
                                accessPoint_data_last_time_down.append(value.created_date)
                                accessPoint_data_last_time_up.append(value.updated_date)


                        elif select_time >= 180 :
                            if value.minutes >= select_time and value.minutes < select_time * 2 :
                                accessPoint_data_name.append(accessPoints.name)   
                                accessPoint_data_minutes.append(value.minutes)
                                accessPoint_data_last_time_down.append(value.created_date)
                                accessPoint_data_last_time_up.append(value.updated_date)


                    elif value.last_state == -2:
                        if value.minutes >= select_time and value.minutes < select_time * 2 :
                                accessPoint_data_name.append(accessPoints.name)   
                                accessPoint_data_minutes.append(value.minutes)
                                accessPoint_data_last_time_down.append(value.created_date)
                                accessPoint_data_last_time_up.append(value.updated_date)

            
            accessPoint_data_down_select = {i: {"accessPoint_name": accessPoint_data_name[i], "accessPoint_minutes": accessPoint_data_minutes[i],
                                "accessPoint_last_time_down": accessPoint_data_last_time_down[i], "accessPoint_last_time_up": accessPoint_data_last_time_up[i]} for i in range(len(accessPoint_data_name))}
            
            unique_accessPoint_data_name = set(accessPoint_data_name)
            unique_count_accessPoint_data_name = len(unique_accessPoint_data_name)
            all_count_down = len(accessPoint_data_name)


    return (
            accessPoint_data_down_select,
            unique_count_accessPoint_data_name,
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
DEFAULT_LAT = 7.0088136
DEFAULT_LNG = 100.498062


@caches.cache.cached(timeout=3600, key_prefix='get_ap_list_with_sla')
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
                group_data = None
                query_ap = models.AccessPointLocation.objects(name=name).first()
                for location in location_data:
                    if item[3] and "Group" in item[3]:
                        group_data = item[3].split(", ")[1].split(": ")[1]
                        if group_data == "Dorm10" and location["location_id"] == "DRM10":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                                    "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                    "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                            "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                            "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                            "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                            "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
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
                        "lat": query_ap["coordinates"][0] if query_ap else DEFAULT_LAT,
                        "lng": query_ap["coordinates"][1] if query_ap else DEFAULT_LNG,
                        "group": "",
                        "availability": get_accessPoint_daily_sla(accessPoint_id)
                    })
    return ap_list


def get_ap_name_list(ap_prop):
    get_ap_list = ap_prop
    if get_ap_list is None:
        get_ap_list = []
    ap_list = []

    for data in get_ap_list:
        for item in data["extensions"]["services_with_info"]:
            if item[0].startswith("AP"):
                name = item[0].split()[1]
                ap_list.append({
                    "name": name,
                })
    return ap_list


def get_host_name_list(host_prop):
    get_host_list = host_prop
    if get_host_list is None:
        get_host_list = []
    host_list = []

    for item in get_host_list:
        name = item["extensions"]["name"]
        host_list.append({
            "name": name,
        })
    return host_list


@caches.cache.cached(timeout=3600, key_prefix='get_all_host_list')
def get_all_host_list(host_prop):
    get_host_list = host_prop
    result = []
    for item in get_host_list:
        query_host = models.HostLocation.objects(name=item["extensions"]["name"]).first()
        result.append({
            "host_id": item["id"],
            "title": item["title"],
            "address": item["extensions"]["address"] if item["extensions"]["address"] else "",
            "name": item["extensions"]["name"],
            "state": item["extensions"]["state"],
            "lat": query_host["coordinates"][0] if query_host else DEFAULT_LAT,
            "lng": query_host["coordinates"][1] if query_host else DEFAULT_LNG,
            "groups": item["extensions"]["groups"],
            "availability": get_host_daily_sla(item["id"])
        })
    return result


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
                group_data = None
                query_ap = models.AccessPointLocation.objects(name=name).first()
                for location in location_data:
                    if item[3] and "Group" in item[3]:
                        group_data = item[3].split(", ")[1].split(": ")[1]
                        if group_data == "Dorm10" and location["location_id"] == "DRM10":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm11" and location["location_id"] == "DRM11":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm12" and location["location_id"] == "DRM12":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm13" and location["location_id"] == "DRM13":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm14" and location["location_id"] == "DRM14":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif group_data == "Dorm15" and location["location_id"] == "DRM15":
                            ap_list.append({
                                "accessPoint_id": accessPoint_id,
                                "name": name,
                                "state": state,
                                "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                                "group": location["location_id"]
                            })
                            found_location = True
                            break
                        elif name.startswith(location["location_id"]) and group_data not in DORM_LIST:
                                ap_list.append({
                                    "accessPoint_id": accessPoint_id,
                                    "name": name,
                                    "state": state,
                                    "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                                    "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                                    "group": location["location_id"]
                                })
                                found_location = True
                                break
                        
                    if data["id"] == "WLC" and name.startswith(location["location_id"]) and not name.startswith("DRM15") and not location["location_id"].startswith("DRM15"):
                        ap_list.append({
                            "accessPoint_id": accessPoint_id,
                            "name": name,
                            "state": state,
                            "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                            "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                            "group": location["location_id"]
                        })
                        found_location = True
                        break
                    elif data["id"] == "WLC" and name.startswith("DRM15") and location["location_id"].startswith("DRM15"):
                        ap_list.append({
                            "accessPoint_id": accessPoint_id,
                            "name": name,
                            "state": state,
                            "lat": query_ap["coordinates"][0] if query_ap else location["lat"],
                            "lng": query_ap["coordinates"][1] if query_ap else location["lng"],
                            "group": "DRM15"
                        })
                        found_location = True
                        break
                if not found_location :
                    ap_list.append({
                        "accessPoint_id": accessPoint_id,
                        "name": name,
                        "state": state,
                        "lat":  query_ap["coordinates"][0] if query_ap else DEFAULT_LAT,
                        "lng":  query_ap["coordinates"][1] if query_ap else DEFAULT_LNG,
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
                return '{:.4f}'.format(round(sla, 4))
        
        else :
                return '{:.2f}'.format(round(100, 2))
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
                return '{:.4f}'.format(round(sla, 4))
        
        else :
                return '{:.2f}'.format(round(100, 2))
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
                return '{:.4f}'.format(round(sla, 4))
        
        else :
                return '{:.2f}'.format(round(100, 2))
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
        return '{:.4f}'.format(round(sla / count, 4))
    else:
        return '{:.2f}'.format(round(100, 2))
    
    
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
        return '{:.4f}'.format(round(sla / count, 4))
    else:
        return '{:.2f}'.format(round(100, 2))