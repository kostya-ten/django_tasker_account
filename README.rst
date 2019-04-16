Django Tasker Account - Extended user system for Django 2.x
------------------------------------------------------------------------

Features
""""""""""""""""""
* Geocoding user (Automatic determination of the user's location during registration)
* Automatic time zone change depending on user settings
* Automatic language change depending on user settings  
* User Profile
   * Timezone
   * Language
   * Gender
   * Birth date
   * Mobile phone
   * Avatar
* OAuth
   * Provider
      * Yandex
      * Mail.ru
      * Facebook
      * Google
      * VK.com   
   * Filling user profile from provider OAuth
   * Automatic download avatar
* 2FA

Configuring
""""""""""""""""""

.. table:: Tasker Account recognises the following options.

    ==================== =========== =================================================================================================
    Option               Default     Description
    ==================== =========== =================================================================================================
    YANDEX_MAP_KEY       *Required*  The Geocoder can get a geo object's coordinates
    YANDEX_LOCATOR_KEY   None        Locator locates the user
    GEOIP_PATH           *Required*  Geolocation with GeoIP2  `documentation  <https://docs.djangoproject.com/en/dev/ref/contrib/gis/geoip2/>`_
    EMAIL_HOST           *Required*
    ==================== =========== =================================================================================================

Where to get the keys?
""""""""""""""""""
YANDEX_MAP_KEY - https://tech.yandex.com/maps/

YANDEX_LOCATOR_KEY - https://tech.yandex.ru/locator/ (Russian)
