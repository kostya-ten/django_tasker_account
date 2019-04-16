Django Tasker Account - Extended user system for Django 2.x
------------------------------------------------------------------------

Configuring
""""""""""""""""""

.. table:: Tasker Account recognises the following options.

    ==================== =========== =================================================================================================
    Option               Default     Description
    ==================== =========== =================================================================================================
    YANDEX_MAP_KEY       *Required*  The Geocoder can get a geo object's coordinates
    YANDEX_LOCATOR_KEY   None        Locator locates the user
    GEOIP_PATH           *Required*  Geolocation with GeoIP2  `see  <https://docs.djangoproject.com/en/dev/ref/contrib/gis/geoip2//>`_
    ==================== =========== =================================================================================================

Where to get the keys?
""""""""""""""""""
YANDEX_MAP_KEY - https://tech.yandex.com/maps/

YANDEX_LOCATOR_KEY - https://tech.yandex.ru/locator/ (Russian)
