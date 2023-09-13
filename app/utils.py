from . import models
import requests
from flask_login import current_user
from . import caches
import os
from dotenv import load_dotenv
import httpx
import datetime
import json
import requests

load_dotenv()

API_URL = f"https://{os.environ['HOST_NAME']}/{os.environ['SITE_NAME']}/check_mk/api/1.0"
HEADERS = {
    'Authorization': f"Bearer {os.environ['CHECKMK_USERNAME']} {os.environ['CHECKMK_PASSWORD']}",
    'Accept': 'application/json'
}

url = 'https://notify-api.line.me/api/notify'
token = '4qg3p8FPpB9m4RWmt60mAKoyTdrfItSqovqvKO6mcIE'
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}

def status_list():
    return [
        'PENDING',
        'CHECKING',
        'APPROVED',
        'REJECTED',
    ]


@caches.cache.cached(timeout=3600, key_prefix='location_list')
def location_list():
    return models.Location.objects().order_by("name")


def host_list():
    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', 'groups', 'address'],
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


def service_list(api_hostgroup_url):
    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', 'groups'],
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


def cal_min_down(down_time):

    print("in fuction")
    date = datetime.datetime.now()
    current_time = int(date.timestamp())
    time_difference_seconds = current_time - down_time
    # print("convert success : ", time_difference_seconds)
    #time_difference_seconds = int(int(time_difference.total_seconds())/60)
    time_difference_minute = int(int(time_difference_seconds)/60)

    # print("Time Difference:", (time_difference_minute))
    # print("Time Difference in Seconds:", time_difference_seconds)

    return time_difference_minute

def cal_sla(month,year,sum_min):
    start_date = datetime.datetime(year, month, 1, 0, 1)
    current_date = datetime.datetime.now()
    time_difference = current_date - start_date
    total_minutes = int(time_difference.total_seconds() / 60)
    sla = ((total_minutes - sum_min)/total_minutes) * 100
    return sla
    
   


def host_down_handler():
    try:
        response = requests.get("http://localhost:3000/api/hosts")
        response = response.json()
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        if response:
            for item in response['value']:
                ip_address = item['extensions']['attributes']['ipaddress']
                lat = item['extensions']['attributes']['labels']['lat']
                lng = item['extensions']['attributes']['labels']['lng']
                floor = item['extensions']['attributes']['labels']['floor']
                room = item['extensions']['attributes']['labels']['room']
                state = item['extensions']['last_state']
                host_id = item['title']
            
                print("Host : ",host_id ," state : " , state)
                #! Host DOWN
                if state == 1:
                    
                    host = models.Host.objects(host_id=host_id, month=month, year=year).first()
                    if host:
                        host_list_ids = host.host_list
                        if not host_list_ids:
                            return
                        last_host_list_id = host_list_ids[-1]
                        host_list = models.HostList.objects(id=last_host_list_id.id, last_state=5).first()
                        #? ตัวที่ Down แต่ยังไม่แก้ก็ให้ update last_time_down ไว้ calculate SLA
                        if host_list:
                            print("still have")
                            #TODO  ตรงนี้อาจจะเขียน check if host_list.updated_date == today ถ้าไม่ใช่ก็ให้ส่ง line notify อีก
                            #host_list.last_time_down = datetime.datetime.now()
                            #host_list.save()  
                        else:
                            print("add new one")
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=5,
                                notified=False,
                                remark="",
                                last_time_up=datetime.datetime.now(),
                                last_time_down=datetime.datetime.now(),
                                hour=0,
                            )
                            #TODO  ตรงนี้ให้เขียนส่ง LINE NOTIFY แล้วก็ให้ update notified เป็น True ถ้าส่ง req notify สำเร็จ
                            new_host_list.save()
                            host.host_list.append(new_host_list)
                            host.save()

                            time = datetime.datetime.now()
                            format_time = time.strftime('%Y-%m-%d %H:%M')
                            msg = "\nHost : " + host_id + "\nState : " + "down" + "\nTime Down : " + format_time
                            r = requests.post(url, headers=headers, data = {'message':msg})
                    else:
                        #print("Working2 !!!!")
                        new_host_list = models.HostList(
                            state=int(state),
                            last_state=5,
                            notified=False,
                            remark="",
                            last_time_up=datetime.datetime.now(),
                            last_time_down=datetime.datetime.now(),
                            hour=0,
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
                            coordinates= (lat, lng),
                            floor=floor,
                            room=room,
                            host_list=[
                                new_host_list.id,
                            ],
                        )
                        new_host.save()
                #! Host UP
                elif state == 0:
                    #TODO  ตรงนี้มันน่าจะมีปัญหาเช่น host down ไปเดือนนึง พอขึ้นเดือนใหม่ปรากฏว่า UP record ที่เก็บก่อนหน้าก็จะไม่ถูก update last_state
                    host = models.Host.objects(host_id=host_id, month=month, year=year).first()
                    if host:
                        host_list_ids = host.host_list
                        if not host_list_ids:
                            return
                        last_host_list_id = host_list_ids[-1]
                        host_list = models.HostList.objects(id=last_host_list_id.id, last_state=5).first()
                        if host_list :
                            last_time_down = host_list.last_time_down
                            unix_timestamp = int(last_time_down.timestamp())                         
                            minute = cal_min_down(unix_timestamp)
                            print("min in main = " , minute)
                            host_list.last_state = 0
                            host_list.hour = minute
                            host_list.save()

                        if host_list :    
                            host = models.Host.objects(host_id=host_id, month=month, year=year).first()
                            host_list_id = []
                            sum_min = 0
                            
                            for value in host.host_list :
                                host_list_id.append(value.id)
                            
                            query  = models.HostList.objects(id__in=host_list_id)
                            matching_data = query.all()
                            
                            for data in matching_data:
                                sum_min += data.hour
                            print("sum min : ", sum_min)
                            
                            sla = int(cal_sla(month,year,sum_min))
                            host.availability = sla
                            host.save()
                            
                break
            return response['value']
        else:
            return []
    except Exception as ex:
        return None