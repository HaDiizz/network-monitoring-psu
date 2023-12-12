from .. import models
import requests
from flask_login import current_user
from .. import caches
import os
from dotenv import load_dotenv
import httpx
import datetime
from .utils import cal_min_down, cal_sla

load_dotenv()

API_URL = f"https://{os.environ['HOST_NAME']}/{os.environ['SITE_NAME']}/check_mk/api/1.0"
HEADERS = {
    'Authorization': f"Bearer {os.environ['CHECKMK_USERNAME']} {os.environ['CHECKMK_PASSWORD']}",
    'Accept': 'application/json'
}

url = 'https://notify-api.line.me/api/notify'
line_noti_token = os.environ['LINE_NOTI_TOKEN']
headers = {'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + line_noti_token}


def ap_down_handler(ap_list):
    try:
        response = ap_list()
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        if response:    
            for item in response:
                state = item['state']
                ap_name = item['ap_name']
                lat = item['lat']
                lng = item['lng']
                group = item['group']
                if state == 2:
                    accessPoint = models.AccessPoint.objects(
                        name=ap_name, month=month, year=year).first()
                    if accessPoint:
                        accessPoint_list_ids = accessPoint.ap_list
                        if not accessPoint_list_ids:
                            new_ap_list = models.AccessPointList(
                                state=int(state),
                                last_state=-1,
                                notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_ap_list.save()
                            accessPoint.ap_list.append(new_ap_list)
                            count_down = accessPoint.count + 1
                            accessPoint.count = count_down
                            accessPoint.save()
                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nAccessPoint : " + ap_name + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                        last_accessPoint_list_id = accessPoint_list_ids[-1]
                        accessPoint_list = models.AccessPointList.objects(
                            id=last_accessPoint_list_id.id, last_state=-1).first()

                        if not accessPoint_list:
                            new_accessPoint_list = models.AccessPointList(
                                state=int(state),
                                last_state=-1,
                                notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_accessPoint_list.save()

                            accessPoint.ap_list.append(new_accessPoint_list)
                            count_down = accessPoint.count + 1
                            accessPoint.count = count_down
                            accessPoint.save()

                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nAccessPoint : " + ap_name + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                    else:
                        new_accessPoint_list = models.AccessPointList(
                            state=int(state),
                            last_state=-1,
                            notified=False,
                            remark="",
                            last_time_up=datetime.datetime.now(),
                            last_time_down=datetime.datetime.now(),
                            minutes=0,
                        )
                        new_accessPoint_list.save()

                        new_accessPoint = models.AccessPoint(
                            name=ap_name,
                            month=month,
                            year=year,
                            count=1,
                            availability=100,
                            ap_list=[
                                new_accessPoint_list.id,
                            ],
                            group=group
                        )
                        new_accessPoint.save()
                elif state == 0:
                    accessPoint = models.AccessPoint.objects(
                        name=ap_name, month=month, year=year).first()
                    if accessPoint:
                        accessPoint_list_ids = accessPoint.ap_list
                        if not accessPoint_list_ids:
                            continue
                        last_accessPoint_list_id = accessPoint_list_ids[-1]
                        accessPoint_list = models.AccessPointList.objects(
                            id=last_accessPoint_list_id.id, last_state=-1).first()
                        if accessPoint_list:
                            last_time_down = accessPoint_list.last_time_down
                            unix_timestamp = int(last_time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)
                            accessPoint_list.last_state = 0
                            accessPoint_list.minutes = minute
                            accessPoint_list.save()

                        if accessPoint_list:
                            accessPoint = models.AccessPoint.objects(
                                name=ap_name, month=month, year=year).first()
                            accessPoint_list_ids = []
                            sum_min = 0

                            for value in accessPoint.ap_list:
                                accessPoint_list_ids.append(value.id)

                            query = models.AccessPointList.objects(
                                id__in=accessPoint_list_ids)
                            matching_data = query.all()

                            for data in matching_data:
                                sum_min += data.minutes
                            sla = float(cal_sla(month, year, sum_min))
                            accessPoint.availability = sla
                            accessPoint.save()
                    else:
                        new_accessPoint = models.AccessPoint(
                            name=ap_name,
                            month=month,
                            year=year,
                            count=0,
                            availability=100,
                            group=group
                        )
                        new_accessPoint.save()
            return response
        else:
            return []
    except Exception as ex:
        return None


def service_down_handler(service_list):
    try:
        # response = service_list()
        # now = datetime.datetime.now()
        # month = now.month
        # year = now.year
        # if response:    
        #     for item in response:
        #         state = item['extensions']['state']
        #         service_id = item['id']
        #         title = item['title']
        #         groups = []
        #         for group_item in item['extensions']['groups']:
        #             groups.append(group_item)
        #         if state == 2:
        #             service = models.Service.objects(
        #                 service_id=service_id, month=month, year=year).first()
        #             if service:
        #                 service_list_ids = service.service_list
        #                 if not service_list_ids:
        #                     new_service_list = models.ServiceList(
        #                         state=int(state),
        #                         last_state=-1,
        #                         notified=False,
        #                         remark="",
        #                         last_time_up=datetime.datetime.now(),
        #                         last_time_down=datetime.datetime.now(),
        #                         minutes=0,
        #                     )

        #                     new_service_list.save()
        #                     service.service_list.append(new_service_list)
        #                     count_down = service.count + 1
        #                     service.count = count_down
        #                     service.save()
        #                     time = datetime.datetime.now()
        #                     format_time = time.strftime('%Y-%m-%d %H:%M')
        #                     msg = "🔴" + "\nService : " + service_id + "\nState : " + \
        #                         "Down" + "\nTime Down : " + format_time
        #                     r = requests.post(
        #                         url, headers=headers, data={'message': msg})
        #                 last_service_list_id = service_list_ids[-1]
        #                 service_list = models.ServiceList.objects(
        #                     id=last_service_list_id.id, last_state=-1).first()

        #                 if not service_list:
        #                     new_service_list = models.ServiceList(
        #                         state=int(state),
        #                         last_state=-1,
        #                         notified=False,
        #                         remark="",
        #                         last_time_up=datetime.datetime.now(),
        #                         last_time_down=datetime.datetime.now(),
        #                         minutes=0,
        #                     )

        #                     new_service_list.save()

        #                     service.service_list.append(new_service_list)
        #                     count_down = service.count + 1
        #                     service.count = count_down
        #                     service.save()

        #                     time = datetime.datetime.now()
        #                     format_time = time.strftime('%Y-%m-%d %H:%M')
        #                     msg = "🔴" + "\nService : " + service_id + "\nState : " + \
        #                         "Down" + "\nTime Down : " + format_time
        #                     r = requests.post(
        #                         url, headers=headers, data={'message': msg})
        #             else:
        #                 new_service_list = models.ServiceList(
        #                     state=int(state),
        #                     last_state=-1,
        #                     notified=False,
        #                     remark="",
        #                     last_time_up=datetime.datetime.now(),
        #                     last_time_down=datetime.datetime.now(),
        #                     minutes=0,
        #                 )
        #                 new_service_list.save()

        #                 new_service = models.Service(
        #                     service_id=service_id,
        #                     name=title,
        #                     month=month,
        #                     year=year,
        #                     count=1,
        #                     availability=100,
        #                     service_list=[
        #                         new_service_list.id,
        #                     ],
        #                 )
        #                 new_service.save()
        #         elif state == 0:
        #             service = models.Service.objects(
        #                 service_id=service_id, month=month, year=year).first()
        #             if service:
        #                 service_list_ids = service.service_list
        #                 if not service_list_ids:
        #                     continue
        #                 last_service_list_id = service_list_ids[-1]
        #                 service_list = models.ServiceList.objects(
        #                     id=last_service_list_id.id, last_state=-1).first()
        #                 if service_list:
        #                     last_time_down = service_list.last_time_down
        #                     unix_timestamp = int(last_time_down.timestamp())
        #                     minute = cal_min_down(unix_timestamp)
        #                     service_list.last_state = 0
        #                     service_list.minutes = minute
        #                     service_list.save()

        #                 if service_list:
        #                     service = models.Service.objects(
        #                         service_id=service_id, month=month, year=year).first()
        #                     service_list_ids = []
        #                     sum_min = 0

        #                     for value in service.service_list:
        #                         service_list_ids.append(value.id)

        #                     query = models.ServiceList.objects(
        #                         id__in=service_list_ids)
        #                     matching_data = query.all()

        #                     for data in matching_data:
        #                         sum_min += data.minutes
        #                     sla = float(cal_sla(month, year, sum_min))
        #                     service.availability = sla
        #                     service.save()
        #             else:
        #                 new_service = models.Service(
        #                     service_id=service_id,
        #                     name=title,
        #                     month=month,
        #                     year=year,
        #                     count=0,
        #                     availability=100,
        #                     groups=groups
        #                 )
        #                 new_service.save()
            # return response
        # else:
            return []
    except Exception as ex:
        return None


# def host_down_handler():
    try:
        response = requests.get("http://localhost:3000/api/hosts")
        response = response.json()
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        hostdown_check = []
        hostdown_now = []

        if response:
            for item in response['value']:
                ip_address = item['extensions']['attributes']['ipaddress']
                lat = item['extensions']['attributes']['labels']['lat']
                lng = item['extensions']['attributes']['labels']['lng']
                floor = item['extensions']['attributes']['labels']['floor']
                room = item['extensions']['attributes']['labels']['room']
                state = item['extensions']['last_state']
                host_id = item['title']
                groups = []
        
                if state == 1:
                    host = models.Host.objects(
                        host_id=host_id, month=month, year=year).first()
                    if host:
                        host_list_ids = host.host_list
                        if not host_list_ids:
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=-1,
                                notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_host_list.save()
                            host.host_list.append(new_host_list)
                            count_down = host.count + 1
                            host.count = count_down
                            host.save()
                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nHost : " + host_id + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})

                        last_host_list_id = host_list_ids[-1]
                        host_list = models.HostList.objects(
                            id=last_host_list_id.id, 
                            last_state=-1).first()

                        if not host_list:
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=-1,
                                notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_host_list.save()

                            host.host_list.append(new_host_list)
                            count_down = host.count + 1
                            host.count = count_down
                            host.save()

                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nHost : " + host_id + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                        else :
                            time_down = host_list.last_time_down
                            unix_timestamp = int(time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)

                            if minute >= 1440 :
                                if host_list.last_state == -1:
                                    host_list.last_state = -2
                                    host_list.minutes = minute
                                    host_list.save()
                                    msg = "🔴" + "\nHost : " + host_id + "\nไม่ต้องจ่ายเงิน"
                                    r = requests.post(
                                        url, headers=headers, data={'message': msg})
                    else:
                        new_host_list = models.HostList(
                            state=int(state),
                            last_state=-1,
                            notified=False,
                            remark="",
                            last_time_up=datetime.datetime.now(),
                            last_time_down=datetime.datetime.now(),
                            minutes=0,
                        )
                        new_host_list.save()

                        new_host = models.Host(
                            host_id=host_id,
                            name=host_id,
                            ip_address=ip_address,
                            month=month,
                            year=year,
                            count=1,
                            availability=100,
                            coordinates=(lat, lng),
                            floor=floor,
                            room=room,
                            host_list=[
                                new_host_list.id,
                            ],
                        )
                        new_host.save()
                elif state == 0:
                    host = models.Host.objects(
                        host_id=host_id, month=month, year=year).first()
                    if host:
                        host_list_ids = host.host_list
                        if not host_list_ids:
                            continue
                        last_host_list_id = host_list_ids[-1]

                        host_list = models.HostList.objects(
                            id=last_host_list_id.id, last_state=-1).first()
                        
                        if not host_list :
                            host_list = models.HostList.objects(
                            id=last_host_list_id.id, last_state=-2).first()

                        if host_list:
                            last_time_down = host_list.last_time_down
                            unix_timestamp = int(last_time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)
                            host_list.last_state = 0
                            host_list.minutes = minute
                            host_list.save()

                        if host_list:
                            host = models.Host.objects(
                                host_id=host_id, month=month, year=year).first()
                            host_list_ids = []
                            sum_min = 0

                            for value in host.host_list:
                                host_list_ids.append(value.id)

                            query = models.HostList.objects(
                                id__in=host_list_ids)
                            matching_data = query.all()

                            for data in matching_data:
                                sum_min += data.minutes
                            sla = float(cal_sla(month, year, sum_min))
                            host.availability = sla
                            host.save()
                    else:
                        new_host = models.Host(
                            host_id=host_id,
                            name=host_id,
                            ip_address=ip_address,
                            month=month,
                            year=year,
                            count=0,
                            availability=100,
                            coordinates=(lat, lng),
                            floor=floor,
                            room=room,
                            groups=groups
                        )
                        new_host.save()
            return response['value']
        else:
            return []
    except Exception as ex:
        return None


def host_down_handler():
    now = datetime.datetime.now()
    minute = now.minute
    hour = now.hour
    day = now.day
    month = now.month
    year = now.year
    hostdown_check = []
    hostdown_now = []

    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name', 'state', 'last_state', 'labels', 'groups', 'address'],
            }
            response = client.get(
                f"{API_URL}/domain-types/host/collections/all",
                headers=HEADERS,
                params=params
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    response = response['value']
            else:
                response = []
        host = models.Host.objects(month=month, year=year).first()
        if 1 == 2: # if (day == 1 and hour == 0 and minute <= 5) or (host is None) : #day == 1 and hour == 0 and minute <= 5
            if response :
                get_host_all(response, month, year)
        
        else :
            response = host_is_down() #! Api get only hosts down
            if response :
                get_host_down(response, month, year, hostdown_check, hostdown_now)

        if response:
            return "Saved Successfully"
        else:
            return []
    except Exception as ex:
        print("Error: ", ex)
        return None


def get_host_all(response, month, year) :

    for item in response:
                ip_address = item['extensions']['address']
                state = item['extensions']['state']
                host_id = item['id']
                host_name = item['title']
                groups = []
                
                for group_item in item['extensions']['groups']:
                    groups.append(group_item)

                if state == 1:
                    host = models.Host.objects(
                        host_id=host_id, month=month, year=year).first()
                    if host:
                        host_list_ids = host.host_list
                        if not host_list_ids:
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=-1,
                                # notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_host_list.save()
                            host.host_list.append(new_host_list)
                            count_down = host.count + 1
                            host.count = count_down
                            host.save()
                            # time = datetime.datetime.now()
                            # format_time = time.strftime('%Y-%m-%d %H:%M')
                            # msg = "🔴" + "\nHost : " + host_id + "\nState : " + \
                            #     "Down" + "\nTime Down : " + format_time
                            # r = requests.post(
                            #     url, headers=headers, data={'message': msg})

                        last_host_list_id = host_list_ids[-1]
                        host_list = models.HostList.objects(
                            id=last_host_list_id.id, 
                            last_state=-1).first()

                        if not host_list:
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=-1,
                                # notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_host_list.save()

                            host.host_list.append(new_host_list)
                            count_down = host.count + 1
                            host.count = count_down
                            host.save()

                            # time = datetime.datetime.now()
                            # format_time = time.strftime('%Y-%m-%d %H:%M')
                            # msg = "🔴" + "\nHost : " + host_id + "\nState : " + \
                            #     "Down" + "\nTime Down : " + format_time
                            # r = requests.post(
                            #     url, headers=headers, data={'message': msg})
                        else :
                            time_down = host_list.last_time_down
                            unix_timestamp = int(time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)

                            if minute >= 1440 :
                                if host_list.last_state == -1:
                                    host_list.last_state = -2
                                    host_list.minutes = minute
                                    host_list.save()
                                    msg = "🔴" + "\nHost : " + host_id + "\nไม่ต้องจ่ายเงิน"
                                    r = requests.post(
                                        url, headers=headers, data={'message': msg})
                    else:
                        new_host_list = models.HostList(
                            state=int(state),
                            last_state=-1,
                            # notified=False,
                            remark="",
                            last_time_up=datetime.datetime.now(),
                            last_time_down=datetime.datetime.now(),
                            minutes=0,
                        )
                        new_host_list.save()

                        new_host = models.Host(
                            host_id=host_id,
                            name=host_name,
                            ip_address=ip_address,
                            month=month,
                            year=year,
                            count=1,
                            availability=100,
                            host_list=[
                                new_host_list.id,
                            ],
                        )
                        new_host.save()
                elif state == 0:
                    host = models.Host.objects(
                        host_id=host_id, month=month, year=year).first()
                    if host:
                        host_list_ids = host.host_list
                        if not host_list_ids:
                            continue
                        last_host_list_id = host_list_ids[-1]

                        host_list = models.HostList.objects(
                            id=last_host_list_id.id, last_state=-1).first()
                        
                        if not host_list :
                            host_list = models.HostList.objects(
                            id=last_host_list_id.id, last_state=-2).first()

                        if host_list:
                            last_time_down = host_list.last_time_down
                            unix_timestamp = int(last_time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)
                            host_list.last_state = 0
                            host_list.minutes = minute
                            host_list.save()

                        if host_list:
                            host = models.Host.objects(
                                host_id=host_id, month=month, year=year).first()
                            host_list_ids = []
                            sum_min = 0

                            for value in host.host_list:
                                host_list_ids.append(value.id)

                            query = models.HostList.objects(
                                id__in=host_list_ids)
                            matching_data = query.all()

                            for data in matching_data:
                                sum_min += data.minutes
                            sla = float(cal_sla(month, year, sum_min))
                            host.availability = sla
                            host.save()
                    else:
                        new_host = models.Host(
                            host_id=host_id,
                            name=host_name,
                            ip_address=ip_address,
                            month=month,
                            year=year,
                            count=0,
                            availability=100,
                            groups=groups
                        )
                        new_host.save()
    print("It's Working !!!")

def get_host_down(response, month, year, hostdown_in_db, hostdown_now) :
    
    for item in response:
                ip_address = item['extensions']['address']
                state = item['extensions']['state']
                host_id = item['id']
                host_name = item['title']
                groups = []

                hostdown = models.HostDown.objects(
                        host_id=host_id).first()
                
                if hostdown :
                    
                    hostdown_now.append(host_id)

                else :

                    new_hostdown = models.HostDown(
                                host_id = host_id,
                                last_time_down=datetime.datetime.now()
                            )

                    new_hostdown.save()
                    hostdown_now.append(host_id)
                
                host = models.Host.objects(
                        host_id=host_id, month=month, year=year).first()
                
                if host:
                        last_id = []
                        host_list_ids = host.host_list
                        for i in host_list_ids :
                            last_id.append(i)
                        serach_id = last_id[-1]
                        
                        print(serach_id)
                        
                        if not host_list_ids:
                            print("if not 1")
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=-1,
                                # notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )
                            print("EEEEEE")
                            new_host_list.save()
                            host.host_list.append(new_host_list)
                            count_down = host.count + 1
                            host.count = count_down
                            host.save()
                            
                            print("QQQQQ")
                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nHost : " + host_id + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                            print("1")
                            print(format_time, host_id)
                            print(headers)
                        last_host_list_id = host_list_ids[-1]
                        host_list = models.HostList.objects(
                            id=last_host_list_id.id, 
                            last_state=-1).first()

                        if not host_list:
                            print("if not 2")
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=-1,
                                # notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_host_list.save()

                            host.host_list.append(new_host_list)
                            count_down = host.count + 1
                            host.count = count_down
                            host.save()

                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nHost : " + host_id + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                            print("2")
                            print(format_time, host_id)
                            print(headers)
                        else :
                            print("else")
                            time_down = host_list.last_time_down
                            unix_timestamp = int(time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)

                            if minute >= 1440 :
                                if host_list.last_state == -1:
                                    host_list.last_state = -2
                                    host_list.minutes = minute
                                    host_list.save()
                                    msg = "🔴" + "\nHost : " + host_id + "\nไม่ต้องจ่ายเงิน"
                                    r = requests.post(
                                        url, headers=headers, data={'message': msg})
                                    print("3")
                                    print(format_time, host_id)
                                    print(headers)
                            if minute >= 1440 :
                                host_list.minutes = minute
                else:
                    new_host_list = models.HostList(
                        state=int(state),
                        last_state=-1,
                        # notified=False,
                        remark="",
                        last_time_up=datetime.datetime.now(),
                        last_time_down=datetime.datetime.now(),
                        minutes=0,
                    )
                    new_host_list.save()

                    new_host = models.Host(
                        host_id=host_id,
                        name=host_name,
                        ip_address=ip_address,
                        month=month,
                        year=year,
                        count=1,
                        availability=100,
                        host_list=[
                            new_host_list.id,
                        ],
                    )
                    new_host.save()

    #Start Here
    all_host = models.HostDown.objects.all()   
    for host in all_host :
        hostdown_in_db.append(host.host_id)
    
    filter_host_down = [host for host in hostdown_now if host not in hostdown_in_db]
    
    for host_id in filter_host_down :

        host = models.Host.objects(
                            host_id=host_id, month=month, year=year).first()
        if host:
            host_list_ids = host.host_list
            if not host_list_ids:
                print()
            last_host_list_id = host_list_ids[-1]

            host_list = models.HostList.objects(
                id=last_host_list_id.id, last_state=-1).first()
            
            if not host_list :
                host_list = models.HostList.objects(
                id=last_host_list_id.id, last_state=-2).first()

            if host_list:
                last_time_down = host_list.last_time_down
                unix_timestamp = int(last_time_down.timestamp())
                minute = cal_min_down(unix_timestamp)
                host_list.last_state = 0
                host_list.minutes = minute
                host_list.save()

            if host_list:
                host = models.Host.objects(
                    host_id=host_id, month=month, year=year).first()
                host_list_ids = []
                sum_min = 0

                for value in host.host_list:
                    host_list_ids.append(value.id)

                query = models.HostList.objects(
                    id__in=host_list_ids)
                matching_data = query.all()

                for data in matching_data:
                    sum_min += data.minutes
                sla = float(cal_sla(month, year, sum_min))
                host.availability = sla
                host.save()
        else:
            new_host = models.Host(
                host_id=host_id,
                name=host_name,
                ip_address=ip_address,
                month=month,
                year=year,
                count=0,
                availability=100,
                groups=groups
            )
            new_host.save()
    
    models.HostDown.objects(id__in=filter_host_down).delete()


def get_host_markers():
    try:
        response = requests.get("http://localhost:3000/api/hosts")
        response = response.json()
        if response:
            for item in response['value']:
                if not current_user.is_authenticated:
                    del item['extensions']['attributes']['ipaddress']
            return response['value']
        else:
            return []
    except Exception as ex:
        return None


def host_list():
    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name', 'state', 'last_state', 'labels', 'groups', 'address'],
            }
            # params = {
            #     "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', 'groups', 'address'],
            # }

            response = client.get(
                f"{API_URL}/domain-types/host/collections/all",
                headers=HEADERS,
                params=params
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    for item in response['value']:
                        if not current_user.is_authenticated or current_user.role != 'admin':
                            del item['extensions']['address']
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None


def service_list():
    try:
        service_groups = []
        response_list = []
        for group in service_group_list():
            service_groups.append(group["id"])
        
        with httpx.Client() as client:
            params = {
                "columns": ['state', 'last_state', 'last_time_ok', 'last_time_critical', 'last_time_unknown', 'last_time_warning', 'last_state_change', 'labels', "groups", 'downtimes_with_extra_info', ],
            }
            for group_name in service_groups:
                response = client.get(
                    f"https://{os.environ['HOST_NAME']}/{os.environ['SITE_NAME']}/check_mk/api/1.0/domain-types/service/collections/all?query=%7B%22op%22%3A+%22%3E%3D%22%2C+%22left%22%3A+%22services.groups%22%2C+%22right%22%3A+%22{group_name}%22%7D",
                    headers=HEADERS,
                    params=params
                )
                if response.status_code == 200:
                    response = response.json()
                    if response:
                        response_list.extend(response['value'])
                else:
                    return []
            dict_of_objects = {}    
            for object in response_list:
                dict_of_objects[object["id"]] = object
            list_of_objects_without_duplicates = list(dict_of_objects.values())
            return list_of_objects_without_duplicates
    except Exception as ex:
        return None


def host_group_list():
    try:
        with httpx.Client() as client:

            response = client.get(
                f"{API_URL}/domain-types/host_group_config/collections/all",
                headers=HEADERS,
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None


def service_group_list():
    try:
        with httpx.Client() as client:

            response = client.get(
                f"{API_URL}/domain-types/service_group_config/collections/all",
                headers=HEADERS,
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None


def host_group(api_hostgroup_url):
    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', 'groups', 'address'],
            }

            response = client.get(
                f"{api_hostgroup_url}",
                headers=HEADERS,
                params=params
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None

def maintain_host_list():
    try:
        with httpx.Client() as client:
            params = {}
            response = client.get(
                f"{os.environ['HOSTS_IN_DOWNTIME']}",
                headers=HEADERS,
                params=params
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None

def maintain_service_list():
    try:
        with httpx.Client() as client:
            params = {}
            response = client.get(
                f"{os.environ['SERVICES_IN_DOWNTIME']}",
                headers=HEADERS,
                params=params
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None
    
def service_is_down():
    try:
        with httpx.Client() as client:
            params = {
                "columns": [ 'host_name', 'state', 'host_groups'],
                "query": '{"op": "!=", "left": "state", "right": "0"}',
            }
            response = client.get(
                f"{API_URL}/domain-types/service/collections/all",
                headers=HEADERS,
                params=params
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None
    

def host_is_down():
    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', "groups", 'address', ],
                "query": '{"op": "!=", "left": "state", "right": "0"}',
            }
            response = client.get(
                f"{API_URL}/domain-types/host/collections/all",
                headers=HEADERS,
                params=params
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None
    
    
def check_access_point():
    try:
        with httpx.Client() as client:
            params = {
                "query": '{"op":"or", "expr": [{"op":"=","left":"hosts.name","right":"WLC"}, {"op":"=","left":"hosts.name","right":"Aruba-Controller"} ]}',
                # "query": '{"op":"=","left":"hosts.name","right":"Aruba-Controller"}',
                "columns": [ 'name', 'state', 'groups','services_with_info',],
            }
            response = client.get(
                f"{API_URL}/domain-types/host/collections/all",
                headers=HEADERS,
                params=params
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    return response['value']
            else:
                return []
    except Exception as ex:
        return None