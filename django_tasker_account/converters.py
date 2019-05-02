from importlib import import_module

from django.conf import settings


class ConfirmEmail:
    regex = '[a-z0-9]+'

    @staticmethod
    def to_python(session_key):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store(session_key=session_key)

        if session is None:
            raise ValueError('Session not found')

        if session.get('module') == 'django_tasker_account.forms':
            session['data']['session'] = session
            return session.get('data')
        else:
            raise ValueError('Session not found')

    @staticmethod
    def to_url(value):
        return value