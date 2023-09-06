from . import models
import requests
from flask_login import current_user
from . import caches
import os
from dotenv import load_dotenv
import httpx

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
                "columns": ['name', 'state', 'last_state', 'last_time_up', 'last_time_down', 'last_time_unreachable', 'last_state_change', 'labels', "groups"],
            }

            resp = client.get(
                f"{API_URL}/domain-types/host/collections/all",
                headers=HEADERS,
                params=params
            )
            if resp.status_code == 200:
                resp = resp.json()
                if resp:
                    return resp['value']
            else:
                return []
    except Exception as ex:
        return None


def service_list():
    try:
        session = requests.session()
        session.headers['Authorization'] = f"Bearer {os.environ['CHECKMK_USERNAME']} {os.environ['CHECKMK_PASSWORD']}"
        session.headers['Accept'] = 'application/json'
        response = session.get(
            f"{API_URL}/domain-types/service/collections/all",
            params={
                "host_name": 'localhost',
                "columns": ['state', 'display_name', 'last_time_ok', 'last_time_critical', 'last_time_unknown', 'last_time_warning'],
            }
        )
        if response.status_code == 200:
            response = response.json()
            if response:
                return response['value']
        else:
            return []
    except Exception as ex:
        return None
