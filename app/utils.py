from . import models


def status_list():
    return [
        'PENDING',
        'CHECKING',
        'APPROVED',
        'REJECTED',
    ]


def location_list():
    return models.Location.objects().order_by("name")
