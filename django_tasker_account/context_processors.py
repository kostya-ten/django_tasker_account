import datetime

from django.conf import settings as data_settings
from django.core.handlers.wsgi import WSGIRequest


def year(request: WSGIRequest):
    return {'YEAR': datetime.datetime.now().year}


def settings(request: WSGIRequest):
    return {
        'SETTINGS': data_settings,
        'DEBUG': data_settings.DEBUG,
    }
