import requests
from flask_login import current_user
import os
from dotenv import load_dotenv
import httpx
from .utils import get_service_daily_sla, get_host_group_monthly_sla, get_service_group_monthly_sla

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