from .. import models
import requests
from flask_login import current_user
import os
from dotenv import load_dotenv
import httpx
import datetime
from .utils import cal_min_down, cal_sla, get_all_ap_list, get_service_daily_sla, get_host_group_monthly_sla, get_service_group_monthly_sla
from bson import ObjectId

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

DEFAULT_LAT = 7.0088136
DEFAULT_LNG = 100.498062


def accessPoint_down_handler():
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    
    try:
        get_ap_data = access_point_list()
        response = get_all_ap_list(get_ap_data)
        accessPoint = models.AccessPoint.objects(month=month, year=year).first()
        if not accessPoint or accessPoint is None :
            if response :
                get_accessPoint_all(response, month, year)
        
        else :
            ap_data_list = []
            get_ap_data = access_point_is_down()
            for item in get_ap_data:
                if item["extensions"]["description"].startswith("AP"):
                    host_name =  item["extensions"]["host_name"]
                    state = int(item["extensions"]["state"])
                    if host_name == "WLC":
                        ap_data_list.append({
                            "id": host_name,
                            "extensions": {
                                "services_with_info":[
                                    [ item["extensions"]["description"], state, '', f"Accesspoint: online" ]
                                ]
                            }
                        })
                    else:
                        group_suffix = item['extensions'].get('description')[-3:]
                        if group_suffix[-1] == 'A':
                            group_prefix = item['extensions'].get('description')[:-2]
                        else:
                            group_prefix = item['extensions'].get('description')[:-3]

                        ap_data_list.append({
                            "id": host_name,
                            "extensions": {
                                "services_with_info": [
                                    [
                                        item["extensions"]["description"],
                                        state,
                                        '',
                                        f"Status: up, Group: { 'Dorm10' if group_prefix == 'DRM10' else 'Dorm11' if group_prefix == 'DRM11' else 'Dorm12' if group_prefix == 'DRM12' else 'Dorm13' if group_prefix == 'DRM13' else 'Dorm14' if group_prefix == 'DRM14' else 'Dorm15' if group_prefix == 'DRM15' else 'Dorm1' if group_prefix == 'DRM1' else 'default'}"
                                    ]
                                ]
                            }
                        })
            response = get_all_ap_list(ap_data_list)
            if response :
                accessPoint_in_db = []
                accessPoint_now = []
                get_accessPoint_down(response, month, year, accessPoint_in_db, accessPoint_now)

        if response:
            return "Saved Successfully"
        else:
            return []
    except Exception as ex:
        print("AccessPoint error: ", ex)
        return None


def get_accessPoint_all(response, month, year) :

    for item in response:
                accessPoint_id = item['accessPoint_id']
                state = item['state']
                lat = item['lat']
                lng = item['lng']
                accessPoint_name = item['name']
                group = item['group']

                if state == 2:
                    accessPoint = models.AccessPoint.objects(
                        accessPoint_id=accessPoint_id, month=month, year=year).first()
                    if accessPoint:
                        accessPoint_list_ids = accessPoint.accessPoint_list
                        if not accessPoint_list_ids:
                            new_accessPoint_list = models.AccessPointList(
                                state=int(state),
                                last_state=-1,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_accessPoint_list.save()
                            accessPoint.accessPoint_list.append(new_accessPoint_list)
                            count_down = accessPoint.count + 1
                            accessPoint.count = count_down
                            accessPoint.save()
                            

                        last_accessPoint_list_id = accessPoint_list_ids[-1]
                        accessPoint_list = models.AccessPointList.objects(
                            id=last_accessPoint_list_id.id, 
                            last_state=-1).first()

                        if not accessPoint_list:
                            new_accessPoint_list = models.AccessPointList(
                                state=int(state),
                                last_state=-1,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_accessPoint_list.save()

                            accessPoint.accessPoint_list.append(new_accessPoint_list)
                            count_down = accessPoint.count + 1
                            accessPoint.count = count_down
                            accessPoint.save()

                        else :
                            time_down = accessPoint_list.last_time_down
                            unix_timestamp = int(time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)

                            if minute >= 1440 :
                                if accessPoint_list.last_state == -1:
                                    accessPoint_list.last_state = -2
                                    accessPoint_list.minutes = minute
                                    accessPoint_list.save()

                                    if len(accessPoint_list_ids) > 0:
                                        accessPoint_all_ids = []
                                        for item_id in accessPoint_list_ids:
                                            if isinstance(item_id, ObjectId):
                                                accessPoint_all_ids.append(item_id.id)
                                            else:
                                                accessPoint_all_ids.append(ObjectId(item_id.id))
                                        query = models.AccessPointList.objects(id__in=accessPoint_all_ids)
                                        matching_data = query.all()
                                        sum_min = 0

                                        for data in matching_data:
                                            sum_min += data.minutes
                                        sla = float(cal_sla(month, year, sum_min))
                                        accessPoint.availability = sla
                                        accessPoint.save()
                    else:
                        new_accessPoint_list = models.AccessPointList(
                            state=int(state),
                            last_state=-1,
                            remark="",
                            last_time_up=datetime.datetime.now(),
                            last_time_down=datetime.datetime.now(),
                            minutes=0,
                        )
                        new_accessPoint_list.save()

                        new_accessPoint = models.AccessPoint(
                            accessPoint_id=accessPoint_id,
                            name=accessPoint_name,
                            month=month,
                            year=year,
                            count=1,
                            availability=100,
                            coordinates=(lat, lng),
                            group=group,
                            floor="",
                            room="",
                            accessPoint_list=[
                                new_accessPoint_list.id,
                            ],
                        )
                        new_accessPoint.save()
                elif state == 0:
                    accessPoint = models.AccessPoint.objects(
                        accessPoint_id=accessPoint_id, month=month, year=year).first()
                    if accessPoint:
                        accessPoint_list_ids = accessPoint.accessPoint_list
                        if not accessPoint_list_ids:
                            continue
                        last_accessPoint_list_id = accessPoint_list_ids[-1]

                        accessPoint_list = models.AccessPointList.objects(
                            id=last_accessPoint_list_id.id, last_state=-1).first()
                        
                        if not accessPoint_list :
                            accessPoint_list = models.AccessPointList.objects(
                            id=last_accessPoint_list_id.id, last_state=-2).first()

                        if accessPoint_list:
                            last_time_down = accessPoint_list.last_time_down
                            unix_timestamp = int(last_time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)
                            accessPoint_list.last_state = 0
                            accessPoint_list.minutes = minute
                            accessPoint_list.save()

                        if accessPoint_list:
                            accessPoint = models.AccessPoint.objects(
                                accessPoint_id=accessPoint_id, month=month, year=year).first()
                            accessPoint_list_ids = []
                            sum_min = 0

                            for value in accessPoint.accessPoint_list:
                                accessPoint_list_ids.append(value.id)

                            if len(accessPoint_list_ids) > 0:
                                accessPoint_all_ids = []
                                for item_id in accessPoint_list_ids:
                                    if isinstance(item_id, ObjectId):
                                        accessPoint_all_ids.append(item_id.id)
                                    else:
                                        accessPoint_all_ids.append(ObjectId(item_id.id))
                                query = models.AccessPointList.objects(id__in=accessPoint_all_ids)
                                matching_data = query.all()

                                for data in matching_data:
                                    sum_min += data.minutes
                                sla = float(cal_sla(month, year, sum_min))
                                accessPoint.availability = sla
                                accessPoint.save()
                    else:
                        new_accessPoint = models.AccessPoint(
                            accessPoint_id=accessPoint_id,
                            name=accessPoint_name,
                            month=month,
                            year=year,
                            count=0,
                            availability=100,
                            coordinates=(lat, lng),
                            group=group,
                            floor="",
                            room="",
                        )
                        new_accessPoint.save()


def get_accessPoint_down(response, month, year, accessPoint_down_in_db, accessPoint_down_now) :
    
    for item in response:
                accessPoint_id = item['accessPoint_id']
                state = item['state']
                lat = item['lat']
                lng = item['lng']
                accessPoint_name = item['name']
                group = item['group']

                accessPoint_down = models.AccessPointDown.objects(
                        accessPoint_id=accessPoint_id).first()
                
                if accessPoint_down :
                    accessPoint_down_now.append(accessPoint_id)

                else :

                    new_accessPoint_down = models.AccessPointDown(
                                accessPoint_id = accessPoint_id,
                                last_time_down=datetime.datetime.now()
                            )

                    new_accessPoint_down.save()
                    accessPoint_down_now.append(accessPoint_id)
                
                accessPoint = models.AccessPoint.objects(
                        accessPoint_id=accessPoint_id, month=month, year=year).first()
                
                if accessPoint:
                        last_id = []
                        accessPoint_list_ids = accessPoint.accessPoint_list
                        

                        if not accessPoint_list_ids:
                            new_accessPoint_list = models.AccessPointList(
                                state=int(state),
                                last_state=-1,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )
                            
                            new_accessPoint_list.save()
                            accessPoint.accessPoint_list.append(new_accessPoint_list)
                            count_down = accessPoint.count + 1
                            accessPoint.count = count_down
                            accessPoint.save()
                            
                            
                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nAccessPoint : " + accessPoint_id + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                            
                        last_accessPoint_list_id = accessPoint_list_ids[-1]
                        accessPoint_list = models.AccessPointList.objects(
                            id=last_accessPoint_list_id.id, 
                            last_state=-1).first()

                        if not accessPoint_list:
                            
                            new_accessPoint_list = models.AccessPointList(
                                state=int(state),
                                last_state=-1,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_accessPoint_list.save()

                            accessPoint.accessPoint_list.append(new_accessPoint_list)
                            count_down = accessPoint.count + 1
                            accessPoint.count = count_down
                            accessPoint.save()

                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nAccessPoint : " + accessPoint_id + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                            
                        else :
                            
                            time_down = accessPoint_list.last_time_down
                            unix_timestamp = int(time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)

                            if minute >= 1440 :
                                if accessPoint_list.last_state == -1:
                                    accessPoint_list.last_state = -2
                                    accessPoint_list.minutes = minute
                                    accessPoint_list.save()

                                    if len(accessPoint_list_ids) > 0:
                                        accessPoint_all_ids = []
                                        for item_id in accessPoint_list_ids:
                                            if isinstance(item_id, ObjectId):
                                                accessPoint_all_ids.append(item_id.id)
                                            else:
                                                accessPoint_all_ids.append(ObjectId(item_id.id))
                                        query = models.AccessPointList.objects(id__in=accessPoint_all_ids)
                                        matching_data = query.all()
                                        sum_min = 0
                                        for data in matching_data:
                                            sum_min += data.minutes
                                        sla = float(cal_sla(month, year, sum_min))
                                        accessPoint.availability = sla
                                        accessPoint.save()
                else:
                    new_accessPoint_list = models.AccessPointList(
                        state=int(state),
                        last_state=-1,
                        remark="",
                        last_time_up=datetime.datetime.now(),
                        last_time_down=datetime.datetime.now(),
                        minutes=0,
                    )
                    new_accessPoint_list.save()

                    new_accessPoint = models.AccessPoint(
                        accessPoint_id=accessPoint_id,
                        name=accessPoint_name,
                        month=month,
                        year=year,
                        count=1,
                        availability=100,
                        coordinates=(lat, lng),
                        group=group,
                        floor="",
                        room="",
                        accessPoint_list=[
                            new_accessPoint_list.id,
                        ],
                    )
                    new_accessPoint.save()

                    time = datetime.datetime.now()
                    format_time = time.strftime('%Y-%m-%d %H:%M')
                    msg = "🔴" + "\nAccessPoint : " + accessPoint_id + "\nState : " + \
                        "Down" + "\nTime Down : " + format_time
                    r = requests.post(
                        url, headers=headers, data={'message': msg})

    all_accessPoint = models.AccessPointDown.objects.all()   
    for accessPoint in all_accessPoint :
        accessPoint_down_in_db.append(accessPoint.accessPoint_id)
    
    filter_accessPoint_down = [accessPoint for accessPoint in accessPoint_down_in_db if accessPoint not in accessPoint_down_now]
    
    for accessPoint_id in filter_accessPoint_down :

        accessPoint = models.AccessPoint.objects(
                            accessPoint_id=accessPoint_id, month=month, year=year).first()
        if accessPoint:
            
            accessPoint_list_ids = accessPoint.accessPoint_list
            last_accessPoint_list_id = accessPoint_list_ids[-1]

            accessPoint_list = models.AccessPointList.objects(
                id=last_accessPoint_list_id.id, last_state=-1).first()
            
            if not accessPoint_list :
                accessPoint_list = models.AccessPointList.objects(
                id=last_accessPoint_list_id.id, last_state=-2).first()

            if accessPoint_list:
                last_time_down = accessPoint_list.last_time_down
                unix_timestamp = int(last_time_down.timestamp())
                minute = cal_min_down(unix_timestamp)
                accessPoint_list.last_state = 0
                accessPoint_list.minutes = minute
                accessPoint_list.save()

            if accessPoint_list:
                accessPoint = models.AccessPoint.objects(
                    accessPoint_id=accessPoint_id, month=month, year=year).first()
                accessPoint_list_ids = []
                sum_min = 0

                for value in accessPoint.accessPoint_list:
                    accessPoint_list_ids.append(value.id)

                if len(accessPoint_list_ids) > 0:
                    accessPoint_all_ids = []
                    for item_id in accessPoint_list_ids:
                        if isinstance(item_id, ObjectId):
                            accessPoint_all_ids.append(item_id)
                        else:
                            accessPoint_all_ids.append(ObjectId(item_id))
                    query = models.AccessPointList.objects(id__in=accessPoint_all_ids)
                    matching_data = query.all()

                    for data in matching_data:
                        sum_min += data.minutes
                    sla = float(cal_sla(month, year, sum_min))
                    accessPoint.availability = sla
                    accessPoint.save()
        else:
            new_accessPoint = models.AccessPoint(
                accessPoint_id=accessPoint_id,
                name=accessPoint_name,
                month=month,
                year=year,
                count=0,
                availability=100,
                coordinates=(lat, lng),
                group=group,
                floor="",
                room="",
            )
            new_accessPoint.save()
    
    models.AccessPointDown.objects(accessPoint_id__in=filter_accessPoint_down).delete()


def service_down_handler():
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    
    try:
        response = service_list("ALL")
        if not response or response is None:
            response = []
        service = models.Service.objects(month=month, year=year).first()

        if not service :
            if response :
                get_service_all(response, month, year)
        
        else :
            response = service_list("DOWN")
            if response :
                service_in_db = []
                service_now = []
                get_service_down(response, month, year, service_in_db, service_now)

        if response:
            return "Saved Successfully"
        else:
            return []
    except Exception as ex:
        print("service_down_handler error: ", ex)
        return None


def get_service_all(response, month, year) :

    for item in response:
                state = item['extensions']['state']
                service_id = item['id']
                service_name = item['title']
                groups = []
                
                for group_item in item['extensions']['groups']:
                    groups.append(group_item)

                if state == 2:
                    service = models.Service.objects(
                        service_id=service_id, month=month, year=year).first()
                    if service:
                        service_list_ids = service.service_list
                        if not service_list_ids:
                            new_service_list = models.ServiceList(
                                state=int(state),
                                last_state=-1,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_service_list.save()
                            service.service_list.append(new_service_list)
                            count_down = service.count + 1
                            service.count = count_down
                            service.save()
                            

                        last_service_list_id = service_list_ids[-1]
                        service_list = models.ServiceList.objects(
                            id=last_service_list_id.id, 
                            last_state=-1).first()

                        if not service_list:
                            new_service_list = models.ServiceList(
                                state=int(state),
                                last_state=-1,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_service_list.save()

                            service.service_list.append(new_service_list)
                            count_down = service.count + 1
                            service.count = count_down
                            service.save()

                        else :
                            time_down = service_list.last_time_down
                            unix_timestamp = int(time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)

                            if minute >= 1440 :
                                if service_list.last_state == -1:
                                    service_list.last_state = -2
                                    service_list.minutes = minute
                                    service_list.save()

                                    if len(service_list_ids) > 0:
                                        service_all_ids = []
                                        for item_id in service_list_ids:
                                            if isinstance(item_id, ObjectId):
                                                service_all_ids.append(item_id.id)
                                            else:
                                                service_all_ids.append(ObjectId(item_id.id))
                                        query = models.ServiceList.objects(id__in=service_all_ids)
                                        matching_data = query.all()
                                        sum_min = 0
                                        for data in matching_data:
                                            sum_min += data.minutes
                                        sla = float(cal_sla(month, year, sum_min))
                                        service.availability = sla
                                        service.save()
                    else:
                        new_service_list = models.ServiceList(
                            state=int(state),
                            last_state=-1,
                            remark="",
                            last_time_up=datetime.datetime.now(),
                            last_time_down=datetime.datetime.now(),
                            minutes=0,
                        )
                        new_service_list.save()

                        new_service = models.Service(
                            service_id=service_id,
                            name=service_name,
                            month=month,
                            year=year,
                            count=1,
                            availability=100,
                            service_list=[
                                new_service_list.id,
                            ],
                        )
                        new_service.save()
                elif state == 0:
                    service = models.Service.objects(
                        service_id=service_id, month=month, year=year).first()
                    if service:
                        service_list_ids = service.service_list
                        if not service_list_ids:
                            continue
                        last_service_list_id = service_list_ids[-1]

                        service_list = models.ServiceList.objects(
                            id=last_service_list_id.id, last_state=-1).first()
                        
                        if not service_list :
                            service_list = models.ServiceList.objects(
                            id=last_service_list_id.id, last_state=-2).first()

                        if service_list:
                            last_time_down = service_list.last_time_down
                            unix_timestamp = int(last_time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)
                            service_list.last_state = 0
                            service_list.minutes = minute
                            service_list.save()

                        if service_list:
                            service = models.Service.objects(
                                service_id=service_id, month=month, year=year).first()
                            service_list_ids = []
                            sum_min = 0

                            for value in service.service_list:
                                service_list_ids.append(value.id)

                            if len(service_list_ids) > 0:
                                service_all_ids = []
                                for item_id in service_list_ids:
                                    if isinstance(item_id, ObjectId):
                                        service_all_ids.append(item_id.id)
                                    else:
                                        service_all_ids.append(ObjectId(item_id.id))
                                query = models.ServiceList.objects(id__in=service_all_ids)
                                matching_data = query.all()

                                for data in matching_data:
                                    sum_min += data.minutes
                                sla = float(cal_sla(month, year, sum_min))
                                service.availability = sla
                                service.save()
                    else:
                        new_service = models.Service(
                            service_id=service_id,
                            name=service_name,
                            month=month,
                            year=year,
                            count=0,
                            availability=100,
                            groups=groups
                        )
                        new_service.save()


def get_service_down(response, month, year, servicedown_in_db, servicedown_now) :
    
    for item in response:
                state = item['extensions']['state']
                service_id = item['id']
                service_name = item['title']
                groups = []

                servicedown = models.ServiceDown.objects(
                        service_id=service_id).first()
                
                if servicedown :
                    
                    servicedown_now.append(service_id)

                else :

                    new_servicedown = models.ServiceDown(
                                service_id = service_id,
                                last_time_down=datetime.datetime.now()
                            )

                    new_servicedown.save()
                    servicedown_now.append(service_id)
                
                service = models.Service.objects(
                        service_id=service_id, month=month, year=year).first()
                
                if service:
                        last_id = []
                        service_list_ids = service.service_list
                        

                        if not service_list_ids:
                            new_service_list = models.ServiceList(
                                state=int(state),
                                last_state=-1,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )
                            
                            new_service_list.save()
                            service.service_list.append(new_service_list)
                            count_down = service.count + 1
                            service.count = count_down
                            service.save()
                            
                            
                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nService : " + service_id + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                            
                        last_service_list_id = service_list_ids[-1]
                        service_list = models.ServiceList.objects(
                            id=last_service_list_id.id, 
                            last_state=-1).first()

                        if not service_list:
                            
                            new_service_list = models.ServiceList(
                                state=int(state),
                                last_state=-1,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                minutes=0,
                            )

                            new_service_list.save()

                            service.service_list.append(new_service_list)
                            count_down = service.count + 1
                            service.count = count_down
                            service.save()

                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "🔴" + "\nService : " + service_id + "\nState : " + \
                                "Down" + "\nTime Down : " + format_time
                            r = requests.post(
                                url, headers=headers, data={'message': msg})
                            
                        else :
                            
                            time_down = service_list.last_time_down
                            unix_timestamp = int(time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)

                            if minute >= 1440 :
                                if service_list.last_state == -1:
                                    service_list.last_state = -2
                                    service_list.minutes = minute
                                    service_list.save()

                                    if len(service_list_ids) > 0:
                                        service_all_ids = []
                                        for item_id in service_list_ids:
                                            if isinstance(item_id, ObjectId):
                                                service_all_ids.append(item_id.id)
                                            else:
                                                service_all_ids.append(ObjectId(item_id.id))
                                        query = models.ServiceList.objects(id__in=service_all_ids)
                                        matching_data = query.all()
                                        sum_min = 0
                                        for data in matching_data:
                                            sum_min += data.minutes
                                        sla = float(cal_sla(month, year, sum_min))
                                        service.availability = sla
                                        service.save()
                else:
                    new_service_list = models.ServiceList(
                        state=int(state),
                        last_state=-1,
                        remark="",
                        last_time_up=datetime.datetime.now(),
                        last_time_down=datetime.datetime.now(),
                        minutes=0,
                    )
                    new_service_list.save()

                    new_service = models.Service(
                        service_id=service_id,
                        name=service_name,
                        month=month,
                        year=year,
                        count=1,
                        availability=100,
                        service_list=[
                            new_service_list.id,
                        ],
                    )
                    new_service.save()

                    time = datetime.datetime.now()
                    format_time = time.strftime('%Y-%m-%d %H:%M')
                    msg = "🔴" + "\nService : " + service_id + "\nState : " + \
                        "Down" + "\nTime Down : " + format_time
                    r = requests.post(
                        url, headers=headers, data={'message': msg})

    all_service = models.ServiceDown.objects.all()   
    for service in all_service :
        servicedown_in_db.append(service.service_id)
    
    filter_service_down = [service for service in servicedown_in_db if service not in servicedown_now]
    
    for service_id in filter_service_down :

        service = models.Service.objects(
                            service_id=service_id, month=month, year=year).first()
        if service:
            
            service_list_ids = service.service_list
            last_service_list_id = service_list_ids[-1]

            service_list = models.ServiceList.objects(
                id=last_service_list_id.id, last_state=-1).first()
            
            if not service_list :
                service_list = models.ServiceList.objects(
                id=last_service_list_id.id, last_state=-2).first()

            if service_list:
                last_time_down = service_list.last_time_down
                unix_timestamp = int(last_time_down.timestamp())
                minute = cal_min_down(unix_timestamp)
                service_list.last_state = 0
                service_list.minutes = minute
                service_list.save()

            if service_list:
                service = models.Service.objects(
                    service_id=service_id, month=month, year=year).first()
                service_list_ids = []
                sum_min = 0

                for value in service.service_list:
                    service_list_ids.append(value.id)

                if len(service_list_ids) > 0:
                    service_all_ids = []
                    for item_id in service_list_ids:
                        if isinstance(item_id, ObjectId):
                            service_all_ids.append(item_id)
                        else:
                            service_all_ids.append(ObjectId(item_id))
                    query = models.ServiceList.objects(id__in=service_all_ids)
                    matching_data = query.all()

                    for data in matching_data:
                        sum_min += data.minutes
                    sla = float(cal_sla(month, year, sum_min))
                    service.availability = sla
                    service.save()
        else:
            new_service = models.Service(
                service_id=service_id,
                name=service_name,
                month=month,
                year=year,
                count=0,
                availability=100,
                groups=groups
            )
            new_service.save()
    
    models.ServiceDown.objects(service_id__in=filter_service_down).delete()


def host_down_handler():
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    
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
        
        if not host :
            if response :
                get_host_all(response, month, year)
        
        else :
            response = host_is_down()
            if response :
                hostdown_in_db = []
                hostdown_now = []
                get_host_down(response, month, year, hostdown_in_db, hostdown_now)

        if response:
            return "Saved Successfully"
        else:
            return []
    except Exception as ex:
        print("host_down_handler error: ", ex)
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
                            

                        last_host_list_id = host_list_ids[-1]
                        host_list = models.HostList.objects(
                            id=last_host_list_id.id, 
                            last_state=-1).first()

                        if not host_list:
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=-1,
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

                        else :
                            time_down = host_list.last_time_down
                            unix_timestamp = int(time_down.timestamp())
                            minute = cal_min_down(unix_timestamp)

                            if minute >= 1440 :
                                if host_list.last_state == -1:
                                    host_list.last_state = -2
                                    host_list.minutes = minute
                                    host_list.save()

                                    if len(host_list_ids) > 0:
                                        host_all_ids = []
                                        for item_id in host_list_ids:
                                            if isinstance(item_id, ObjectId):
                                                host_all_ids.append(item_id.id)
                                            else:
                                                host_all_ids.append(ObjectId(item_id.id))
                                        query = models.HostList.objects(id__in=host_all_ids)
                                        matching_data = query.all()
                                        sum_min = 0
                                        for data in matching_data:
                                            sum_min += data.minutes
                                        sla = float(cal_sla(month, year, sum_min))
                                        host.availability = sla
                                        host.save()
                    else:
                        new_host_list = models.HostList(
                            state=int(state),
                            last_state=-1,
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
                            coordinates=(DEFAULT_LAT, DEFAULT_LNG),
                            floor="",
                            room="",
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

                            if len(host_list_ids) > 0:
                                host_all_ids = []
                                for item_id in host_list_ids:
                                    if isinstance(item_id, ObjectId):
                                        host_all_ids.append(item_id.id)
                                    else:
                                        host_all_ids.append(ObjectId(item_id.id))
                                query = models.HostList.objects(id__in=host_all_ids)
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
                            coordinates=(DEFAULT_LAT, DEFAULT_LNG),
                            floor="",
                            room="",
                            groups=groups
                        )
                        new_host.save()


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
                        

                        if not host_list_ids:
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=-1,
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

                                    if len(host_list_ids) > 0:
                                        host_all_ids = []
                                        for item_id in host_list_ids:
                                            if isinstance(item_id, ObjectId):
                                                host_all_ids.append(item_id.id)
                                            else:
                                                host_all_ids.append(ObjectId(item_id.id))
                                        query = models.HostList.objects(id__in=host_all_ids)
                                        matching_data = query.all()
                                        sum_min = 0
                                        for data in matching_data:
                                            sum_min += data.minutes
                                        sla = float(cal_sla(month, year, sum_min))
                                        host.availability = sla
                                        host.save()
                else:
                    new_host_list = models.HostList(
                        state=int(state),
                        last_state=-1,
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
                        coordinates=(DEFAULT_LAT, DEFAULT_LNG),
                        floor="",
                        room="",
                        host_list=[
                            new_host_list.id,
                        ],
                    )
                    new_host.save()

                    time = datetime.datetime.now()
                    format_time = time.strftime('%Y-%m-%d %H:%M')
                    msg = "🔴" + "\nHost : " + host_id + "\nState : " + \
                        "Down" + "\nTime Down : " + format_time
                    r = requests.post(
                        url, headers=headers, data={'message': msg})

    all_host = models.HostDown.objects.all()   
    for host in all_host :
        hostdown_in_db.append(host.host_id)
    
    filter_host_down = [host for host in hostdown_in_db if host not in hostdown_now]
    

    for host_id in filter_host_down :

        host = models.Host.objects(
                            host_id=host_id, month=month, year=year).first()
        if host:

            host_list_ids = host.host_list
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

                if len(host_list_ids) > 0:
                    host_all_ids = []
                    for item_id in host_list_ids:
                        if isinstance(item_id, ObjectId):
                            host_all_ids.append(item_id)
                        else:
                            host_all_ids.append(ObjectId(item_id))
                    query = models.HostList.objects(id__in=host_all_ids)
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

    models.HostDown.objects(host_id__in=filter_host_down).delete()


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


def host_list_info():
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
                    for item in response['value']:
                        if not current_user.is_authenticated or current_user.role != 'admin':
                            del item['extensions']['address']
                    return response['value']
            else:
                return []
    except Exception as ex:
        print("host_list_info", ex)
        return None
    

def host_list():
    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name'],
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
        print("host_list", ex)
        return None


def service_list(service_state_selector):
    try:
        service_groups = []
        response_list = []
        for group in service_group_list(False):
            service_groups.append(group["id"])
        
        with httpx.Client() as client:
            for group_name in service_groups:
                if service_state_selector == "DOWN":
                    params = {
                        "columns": ['state', 'last_state', 'last_time_ok', 'last_time_critical', 'last_time_unknown', 'last_time_warning', 'last_state_change', 'labels', "groups", 'downtimes_with_extra_info', ],
                    }
                    query = '{"op": "and", "expr": [{"op":">=","left":"services.groups","right":"'+ group_name +'"},{"op": "=", "left": "services.state", "right":"2"}]}'
                else:
                    params = {
                        "columns": ['state', 'last_state', 'last_time_ok', 'last_time_critical', 'last_time_unknown', 'last_time_warning', 'last_state_change', 'labels', "groups", 'downtimes_with_extra_info', ],
                    }
                    query = f"%7B%22op%22%3A+%22%3E%3D%22%2C+%22left%22%3A+%22services.groups%22%2C+%22right%22%3A+%22{group_name}%22%7D"
                response = client.get(
                    f"https://{os.environ['HOST_NAME']}/{os.environ['SITE_NAME']}/check_mk/api/1.0/domain-types/service/collections/all?query={query}",
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
        print('service_list', ex)
        return None


def get_all_service_list():
    try:
        service_groups = []
        response_list = []
        for group in service_group_list(False):
            service_groups.append(group["id"])
        
        with httpx.Client() as client:
            for group_name in service_groups:
                params = {
                    "columns": ['state', 'last_state', 'last_time_ok', 'last_time_critical', 'last_time_unknown', 'last_time_warning', 'last_state_change', 'labels', "groups", 'downtimes_with_extra_info', ],
                }
                query = f"%7B%22op%22%3A+%22%3E%3D%22%2C+%22left%22%3A+%22services.groups%22%2C+%22right%22%3A+%22{group_name}%22%7D"
                response = client.get(
                    f"https://{os.environ['HOST_NAME']}/{os.environ['SITE_NAME']}/check_mk/api/1.0/domain-types/service/collections/all?query={query}",
                    headers=HEADERS,
                    params=params
                )
                if response.status_code == 200:
                    response = response.json()
                    if response:
                        for item in response['value']:
                            item['extensions']['availability'] = get_service_daily_sla(item["id"])
                        response_list.extend(response['value'])
                else:
                    return []
            dict_of_objects = {}    
            for object in response_list:
                dict_of_objects[object["id"]] = object
            list_of_objects_without_duplicates = list(dict_of_objects.values())
            return list_of_objects_without_duplicates
    except Exception as ex:
        print('get_all_service_list', ex)
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
                    for item in response['value']:
                        item['extensions']['availability'] = get_host_group_monthly_sla(item["id"])
                    return response['value']
            else:
                return []
    except Exception as ex:
        print('host_group_list', ex)
        return None


def service_group_list(is_select_sla):
    try:
        with httpx.Client() as client:

            response = client.get(
                f"{API_URL}/domain-types/service_group_config/collections/all",
                headers=HEADERS,
            )
            if response.status_code == 200:
                response = response.json()
                if response:
                    if is_select_sla:
                        for item in response['value']:
                            item['extensions']['availability'] = get_service_group_monthly_sla(item["id"])
                    return response['value']
            else:
                return []
    except Exception as ex:
        print('service_group_list', ex)
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
                "query": '{"op": "=", "left": "state", "right": "2"}',
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
        print("service_is_down", ex)
        return None
    

def host_is_down():
    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', "groups", 'address', ],
                "query": '{"op": "=", "left": "state", "right": "1"}',
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
        print("host_is_down", ex)
        return None
    
    
def access_point_list():
    try:
        with httpx.Client() as client:
            params = { 
                "query": '{"op":"or", "expr": [{"op":"=","left":"hosts.name","right":"WLC"}, {"op":"=","left":"hosts.name","right":"Aruba-Controller"} ]}',
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
        print("access_point_list", ex)
        return None

 
def access_point_is_down():
    try:
        with httpx.Client() as client:
            params = { 
                    "query": '{"op": "and", "expr": [{"op":"or", "expr": [{"op":"=","left":"services.host_name","right":"WLC"}, {"op":"=","left":"services.host_name","right":"Aruba-Controller"} ]},{"op": "=", "left": "services.state", "right":"2"}]}',
                    "columns": [ 'host_name', 'state', 'description'],
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
        print("access_point_is_down", ex)
        return None
    
def ap_in_downtime():
    try:
        with httpx.Client() as client:
            params = { 
                "query": '{"op":"and","expr":[{"op":"or", "expr": [{"op":"=","left":"services.host_name","right":"WLC"}, {"op":"=","left":"services.host_name","right":"Aruba-Controller"} ]},{"op":"or","expr":[{"op":">","left":"services.scheduled_downtime_depth","right":"0"},{"op":">","left":"services.host_scheduled_downtime_depth","right":"0"}]}]}',
                "columns": [ 'host_name', 'state','description',],
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
        print("ap_in_downtime", ex)
        return None