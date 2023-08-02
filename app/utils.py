from . import models
import requests
from flask_login import current_user


def status_list():
    return [
        'PENDING',
        'CHECKING',
        'APPROVED',
        'REJECTED',
    ]


def location_list():
    return models.Location.objects().order_by("name")


def host_list():
    try:
        response = requests.get("https://nwms-cms-api.onrender.com/api/hosts")
        response = response.json()
        for item in response['value']:
            if not current_user.is_authenticated:
                del item['extensions']['attributes']['ipaddress']
        return response['value']
    except Exception as ex:
        return {"msg": "error"}
