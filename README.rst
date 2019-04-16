Django Tasker Account - Extended user system for Django 2.x
------------------------------------------------------------------------

.. image:: https://travis-ci.org/kostya-ten/django_tasker_account.svg?branch=master
    :target: https://travis-ci.org/kostya-ten/django_tasker_account
    
    
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
* Pages
   * Login page
   * Sign up page (sending a confirmation email)
   * Page forgot password
   * User profile page
      * Page change password
      * Page change firstname, lastname, gender, birth date
      * Page change country and city
      * Set 2FA
      * Upload avatar

Requirements
""""""""""""""""""
* Python 3.6+
* A supported version of Django (currently 2.2)

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
