Welcome to Django Tasker Account's documentation!
=================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. image:: https://travis-ci.org/kostya-ten/django_tasker_account.svg?branch=master
    :target: https://travis-ci.org/kostya-ten/django_tasker_account

.. image:: https://readthedocs.org/projects/django-tasker-account/badge/?version=latest
    :target: https://django-tasker-account.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://api.codacy.com/project/badge/Grade/512d4c90fc16438a9063d08bdec48641
    :target: https://www.codacy.com/app/kostya-ten/django_tasker_account?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kostya-ten/django_tasker_account&amp;utm_campaign=Badge_Grade
    :alt: Codacy Badge

.. image:: https://requires.io/github/kostya-ten/django_tasker_account/requirements.svg?branch=master
     :target: https://requires.io/github/kostya-ten/django_tasker_account/requirements/?branch=master
     :alt: Requirements Status


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

Getting It
""""""""""""""""""

You can get Django Tasker Account by using pip::

    $ pip install django-tasker-account

If you want to install it from source, grab the git repository from GitHub and run setup.py::

    $ git clone git://github.com/kostya-ten/django_tasker_account.git
    $ cd django_tasker_account
    $ python setup.py install


Installation
""""""""""""""""""
To enable ``django_tasker_account`` in your project you need to add it to `INSTALLED_APPS` in your projects ``settings.py``

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'django_tasker_account',
        # ...
    )


Configuring
""""""""""""""""""

.. table:: Django Tasker Account recognises the following options.

    ============================== =========== =================================================================================================
    Option                         Default     Description
    ============================== =========== =================================================================================================
    YANDEX_MAP_KEY                 *Required*  The Geocoder can get a geo object's coordinates
    YANDEX_LOCATOR_KEY             *Optional*  Locator locates the user
    GEOIP_PATH                     *Required*  Geolocation with GeoIP2  `documentation  <https://docs.djangoproject.com/en/dev/ref/contrib/gis/geoip2/>`_
    EMAIL_HOST                     *Required*
    TASKER_HTML_INPUT_CLASS        *Optional*  Class html input form
    TASKER_ACCOUNT_SESSION_SIGNUP  1 day
    ============================== =========== =================================================================================================

Where to get the keys?
""""""""""""""""""""""
YANDEX_MAP_KEY - https://tech.yandex.com/maps/

YANDEX_LOCATOR_KEY - https://tech.yandex.ru/locator/ (Russian)

.. toctree::
   :maxdepth: 2
   :caption: Modules:

   geobase
   validators
   views
   models
   forms

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


