from . import models
import requests
from flask_login import current_user
from . import caches
import os
from dotenv import load_dotenv
import httpx
import datetime

load_dotenv()

API_URL = f"https://{os.environ['HOST_NAME']}/{os.environ['SITE_NAME']}/check_mk/api/1.0"
HEADERS = {
    'Authorization': f"Bearer {os.environ['CHECKMK_USERNAME']} {os.environ['CHECKMK_PASSWORD']}",
    'Accept': 'application/json'
}

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
                "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', "groups", 'address'],
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


def service_list():
    try:
        with httpx.Client() as client:
            params = {
                "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', "groups"],
            }
            
            response = client.get(
                f"https://checkmk.psu.ac.th/PSU/check_mk/api/1.0/domain-types/host/collections/all?query=%7B%22op%22%3A+%22~%22%2C+%22left%22%3A+%22hosts.filename%22%2C+%22right%22%3A+%22%5E%5C%2Fwato%5C%2Fpsu_main_service%5C%2F%22%7D",
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
                
                #! Host DOWN
                if state == 1:
                    host = models.Host.objects(host_id=host_id, month=month, year=year).first()
                    if host:
                        host_list_ids = host.host_list
                        if not host_list_ids:
                            return
                        last_host_list_id = host_list_ids[-1]
                        host_list = models.HostList.objects(id=last_host_list_id.id, last_state=1).first()
                        #? ตัวที่ Down แต่ยังไม่แก้ก็ให้ update last_time_down ไว้ calculate SLA
                        if host_list:
                            #TODO  ตรงนี้อาจจะเขียน check if host_list.updated_date == today ถ้าไม่ใช่ก็ให้ส่ง line notify อีก
                            host_list.last_time_down = datetime.datetime.now()
                            host_list.save()  
                        else:
                            new_host_list = models.HostList(
                                state=int(state),
                                last_state=int(state),
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
                    else:
                        new_host_list = models.HostList(
                            state=int(state),
                            last_state=int(state),
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
                            availability=0,
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
                        host_list = models.HostList.objects(id=last_host_list_id.id, last_state=1).first()
                        host_list.last_state = 0
                        host_list.save()
            return response['value']
        else:
            return []
    except Exception as ex:
        return None