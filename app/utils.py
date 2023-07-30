from . import models


def status_list():
    return [
        'PENDING',
        'CHECKING',
        'APPROVED',
        'REJECTED',
    ]


def address_list():
    return models.Address.objects()
