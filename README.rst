Django Tasker Account - Extended user system for Django 2.x
------------------------------------------------------------------------

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
      * Google
      * Facebook
      * VK.com
      * Yandex
   * Filling user profile from provider OAuth
   * Automatic download avatar
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
        'django_tasker_geobase',
        'mptt',
        # ...
    )



`Full documentation <https://django-tasker-account.readthedocs.io/>`_
