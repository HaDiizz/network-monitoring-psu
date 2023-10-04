from nwms import models
from nwms.web import caches
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


def search_month(start_month, end_month, selected_year):
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


def search_host(start_month, end_month, selected_year, host_name):
    if end_month <= 12:
        query = models.Host.objects(
            host_id=host_name,
            month__gte=start_month,
            month__lte=end_month,
            year__in=[selected_year])
        return query
    if end_month == 13:
        query = models.Host.objects(
            (Q(host_id=host_name) & Q(month=11) & Q(year=selected_year)) | Q(host_id=host_name) & (
                Q(month=12) & Q(year=selected_year)) | Q(host_id=host_name) & (Q(month=1) & Q(year=selected_year + 1))
        )
        return query
    elif end_month == 14:
        query = models.Host.objects(
            (Q(host_id=host_name) & Q(month=12) & Q(year=selected_year)) | Q(host_id=host_name) & (Q(month=1) & Q(
                year=selected_year + 1)) | Q(host_id=host_name) & (Q(month=2) & Q(year=selected_year + 1))
        )
        return query


def search_day_data(matching_data):
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
                        check_day["time"] = check_day["time"] + data.minutes
                        check_day["count"] = check_day["count"] + 1
                        break

                else:
                    date = day
                    time = data.minutes
                    count = 1
                    start_day = {"day": day, "time": time, "count": count}
                    host_day_dict.append(start_day)
                    break

        else:
            date = day
            time = data.minutes
            count = 1
            start_day = {"day": day, "time": time, "count": count}
            host_day_dict.append(start_day)

    return host_day_dict


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


def get_day_data(selected_month, selected_year):
    start_month = selected_month
    end_month = selected_month + 2
    if end_month > 12:
        query = search_month(start_month, end_month, selected_year)
    else:
        query = search_month(start_month, end_month, selected_year)

    host = query.all()

    host_list_id = []
    if host:
        for hosts in host:
            for value in hosts.host_list:
                if value.last_state != -1:
                    host_list_id.append(value.id)

        query = models.HostList.objects(id__in=host_list_id)
        matching_data = query.all()
        host_day_dict = search_day_data(matching_data)
        quarter_month_dict = get_all_quarter_data(
            selected_month, selected_year)

        data_dict = {item['day']: {"date": item['day'], 'sla': round(
            (1440 - (item['time']/item['count']))/1440 * 100, 2)} for item in host_day_dict}

        for key in quarter_month_dict:
            if key in data_dict:
                quarter_month_dict[key]['sla'] = data_dict[key]['sla']

        return quarter_month_dict


def get_quarter_data(selected_month, selected_year):
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
        query = search_month(start_month, end_month, selected_year)
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
            for host in matching_hosts:
                sla += host.availability
                count_down += host.count
                if host.ip_address in host_ip:
                    continue
                else:
                    host_ip.append(host.ip_address)
            sla = sla / len(matching_hosts)
            host_sla.append(sla)
            host_count.append(count_down)
    else:
        query = search_month(start_month, end_month, selected_year)
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
            for host in matching_hosts:
                sla += host.availability
                count_down += host.count
                if host.ip_address in host_ip:
                    continue
                else:
                    host_ip.append(host.ip_address)
            sla = sla / len(matching_hosts)
            host_sla.append(sla)
            host_count.append(count_down)

    if avg_sla != 0:
        avg_sla = avg_sla / count
    card_title = get_name_month(selected_month, selected_year)
    return avg_sla, host_all_count, host_name, host_sla, host_ip, host_count, card_title
