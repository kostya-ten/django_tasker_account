from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class ConfirmEmail:
    regex = '[a-z0-9]+'

    def __init__(self):
        self.session = None
        self.next = '/'

        self.username = None
        self.last_name = None
        self.first_name = None
        self.email = None
        self.password1 = None
        self.password2 = None
        self.module = None

    def to_python(self, session_key):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store(session_key=session_key)

        if session is None:
            raise ValueError('Session not found')

        if session.get('module') == 'django_tasker_account.forms':
            self.username = session.get('username')
            self.last_name = session.get('last_name')
            self.first_name = session.get('first_name')
            self.email = session.get('email')
            self.password1 = session.get('password1')
            self.password2 = session.get('password2')
            self.next = session.get('next')
            self.session = session
            self.module = session.get('module')
            return self
        else:
            raise ValueError('Session not found')

    @staticmethod
    def to_url(value):
        return value


class ChangePassword:
    regex = '[a-z0-9]+'

    def __init__(self):
        self.user_id = None
        self.user = None
        self.session = None
        self.module = None
        self.next = '/'

    def to_python(self, session_key):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store(session_key=session_key)

        if session is None:
            raise ValueError('Session not found')

        if session.get('module') == 'django_tasker_account.forms':
            self.user_id = session.get('user_id')
            self.user = get_object_or_404(User, id=session.get('user_id'))
            self.next = session.get('next')
            self.session = session
            self.module = session.get('module')
            return self
        else:
            raise ValueError('Session not found')

    @staticmethod
    def to_url(value):
        return value


class OAuth:
    regex = '[a-z0-9]+'

    def __init__(self):
        self.provider = None
        self.access_token = None
        self.id = None
        self.birth_date = None
        self.gender = None
        self.avatar = None
        self.last_name = None
        self.first_name = None
        self.email = None
        self.username = None
        self.expires_in = None
        self.next = '/'
        self.session = None

    def to_python(self, session_key):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store(session_key=session_key)

        if session is None:
            raise ValueError('Session not found')

        if session.get('oauth') is None:
            raise ValueError('Session not found')

        if session.get('oauth').get('module') == 'django_tasker_account.views':
            self.provider = session.get('oauth').get('provider')
            self.access_token = session.get('oauth').get('access_token')
            self.id = session.get('oauth').get('id')
            self.birth_date = session.get('oauth').get('birth_date')
            self.gender = session.get('oauth').get('gender')
            self.avatar = session.get('oauth').get('avatar')
            self.last_name = session.get('oauth').get('last_name')
            self.first_name = session.get('oauth').get('first_name')
            self.email = session.get('oauth').get('email')
            self.username = session.get('oauth').get('username')
            self.expires_in = session.get('oauth').get('expires_in')
            self.next = session.get('oauth').get('next', '/')
            self.session = session
            return self
        else:
            raise ValueError('Session not found')

    @staticmethod
    def to_url(value):
        return value
