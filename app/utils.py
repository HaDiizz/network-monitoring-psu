from . import models
import requests
from flask_login import current_user
from . import caches
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = f"http://{os.environ['HOST_NAME']}/{os.environ['SITE_NAME']}/check_mk/api/1.0"


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
