import hashlib
import json
import os

import requests
import logging

from ipaddress import ip_address
from timezonefinder import TimezoneFinder

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest

from . import models

logger = logging.getLogger('django_tasker_account')


def detect_ip(query: WSGIRequest) -> models.Geobase:
    """
    Calculates geolocation by IP address.

    :param query: ip address IPv4 or IPv6.
    :returns: Geobase
    """
    if query and isinstance(query, WSGIRequest):
        x_forwarded_for = query.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = query.META.get('REMOTE_ADDR')
    else:
        ip = query

    try:
        ip = ip_address(ip)
    except ValueError:
        geobase = _geocoder("{longitude},{latitude}".format(latitude="51.507351", longitude="-0.12766"))
        return geobase

    # Cache IP address
    cache_detect = cache.get("{name}-{ip}".format(ip=str(ip), name=__name__))
    if cache_detect:
        logger.debug("Get geobase cached data ip:{ip}, id:{id}".format(ip=str(ip), id=cache_detect))
        return models.Geobase.objects.get(id=cache_detect)

    latitude = None
    longitude = None

    YANDEX_LOCATOR_KEY = getattr(settings, 'YANDEX_LOCATOR_KEY', os.environ.get('YANDEX_LOCATOR_KEY'))
    if ip.version == 4 and ip.is_global and YANDEX_LOCATOR_KEY:
        json_params = json.dumps({
            "common": {
                "version": "1.0",
                "api_key": YANDEX_LOCATOR_KEY,
            },
            "gsm_cells": [],
            "wifi_networks": [],
            "ip": {
                "address_v4": str(ip)
            }
        })
        response = requests.post('https://api.lbs.yandex.net/geolocation', params={'json': json_params})
        locator_result = response.json()
        if response.status_code == 200:
            if locator_result.get('position').get('latitude') and locator_result.get('position').get('longitude'):
                latitude = locator_result.get('position').get('latitude')
                longitude = locator_result.get('position').get('longitude')

    elif ip.version == 4 and ip.is_global:
        g = GeoIP2()
        geoip = g.city(str(ip))
        latitude = geoip.get('latitude')
        longitude = geoip.get('longitude')
    elif ip.version == 6 and ip.is_global:
        g = GeoIP2()
        geoip = g.city(str(ip))
        latitude = geoip.get('latitude')
        longitude = geoip.get('longitude')
    else:
        latitude = '51.507351'
        longitude = '-0.12766'

    # Cache IP address
    geobase = detect_geo("{longitude},{latitude}".format(latitude=latitude, longitude=longitude))
    cache.set("{name}-{ip}".format(ip=str(ip), name=__name__), geobase.id, 60 * 60 * 24 * 30)
    return geobase


def detect_geo(query: str) -> models.Geobase:
    """
    Calculates geolocation an address object.

    :param query: Address or geographical the object
    :returns: Geobase
    """
    cache_key = hashlib.sha256()
    cache_key.update(query.encode('utf-8'))

    cache_geocoder = cache.get("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__))
    if cache_geocoder:
        return get_object_or_404(models.Geobase, id=cache_geocoder)

    en = _geocoder(query, language='en')
    if not en:
        en = {
            'country': 'United Kingdom',
            'province': 'England',
            'locality': 'London',
            'timezone': 'Europe/London',
            'latitude': 51.507351,
            'longitude': -0.127664,
        }

    query_geocoder = "{longitude},{latitude}".format(longitude=en.get('longitude'), latitude=en.get('latitude'))
    ru = _geocoder(query_geocoder, language='ru')

    if not ru:
        en = {
            'country': 'United Kingdom',
            'province': 'England',
            'locality': 'London',
            'timezone': 'Europe/London',
            'latitude': 51.507351,
            'longitude': -0.127664,
        }

        ru = {
            'country': 'Великобритания',
            'province': 'Англия',
            'locality': 'Лондон',
            'timezone': 'Europe/London',
            'latitude': 51.507351,
            'longitude': -0.127664,
        }

    country, created = models.GeobaseCountry.objects.update_or_create(
        en=en.get('country'),
        ru=ru.get('country')
    )
    if created:
        logger.debug("created new country object {en}, {ru}".format(en=en.get('country'), ru=ru.get('country')))

    province, created = models.GeobaseProvince.objects.update_or_create(
        en=en.get('province'),
        ru=ru.get('province')
    )
    if created:
        logger.debug("created new province object {en}, {ru}".format(en=en.get('province'), ru=ru.get('province')))

    locality, created = models.GeobaseLocality.objects.update_or_create(
        en=en.get('locality'),
        ru=ru.get('locality')
    )
    if created:
        logger.debug("created new locality object {en}, {ru}".format(en=en.get('locality'), ru=ru.get('locality')))

    timezone, created = models.GeobaseTimezone.objects.update_or_create(name=en.get('timezone'))
    if created:
        logger.debug("created new timezone object {name}".format(name=en.get('timezone')))

    geobase, created = models.Geobase.objects.update_or_create(
        country=country,
        province=province,
        locality=locality,
        defaults={'timezone': timezone, 'longitude': en.get('longitude'), 'latitude': en.get('latitude')}
    )
    if created:
        logger.debug("created new geo object {country}, {province}, {locality}".format(
            country=country,
            province=province,
            locality=locality
        ))

    cache.set("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__), geobase.id, 60 * 60 * 24 * 30)
    return geobase


def _geocoder(query, language='en'):
    data = {
        'country': 'N/A',
        'province': None,
        'locality': None,
        'timezone': 'UTC',
        'latitude': 0,
        'longitude': 0,
    }

    params = {
        "apikey": getattr(settings, 'YANDEX_MAP_KEY', os.environ.get('YANDEX_MAP_KEY')),
        "format": "json",
        "geocode": query,
        "kind": "locality",
    }

    if language == 'ru':
        params['lang'] = 'ru_RU'
    else:
        params['lang'] = 'en_US'

    response = requests.get('https://geocode-maps.yandex.ru/1.x/', params=params)
    json_yandex_map = response.json()
    if 'error' in json_yandex_map:
        return data

    tf = TimezoneFinder()
    geoobject = json_yandex_map.get('response').get('GeoObjectCollection').get('featureMember')
    for item in geoobject:
        item = item.get('GeoObject')

        if 'Point' in item:
            pos = item.get('Point').get('pos')
            pos = pos.split(" ")

        components = item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('Components')
        for component in components:
            if 'kind' in component and component.get('kind') == 'country':
                data['country'] = component.get('name')
            elif 'kind' in component and component.get('kind') == 'province':
                data['province'] = component.get('name')
            elif 'kind' in component and component.get('kind') == 'locality':
                data['locality'] = component.get('name')

        if not data.get('locality'):
            data['locality'] = data.get('province')

        data['longitude'] = float(pos[0])
        data['latitude'] = float(pos[1])
        data['timezone'] = tf.timezone_at(lng=data.get('longitude'), lat=data.get('latitude'))
        return data
