from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, override_settings, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail

from django_tasker_account import forms, views


class Request:

    @classmethod
    def generate_request(self, request):
        # adding session
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        # adding messages
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class Signup(TestCase, Request):
    def test_views(self):
        factory = RequestFactory(HTTP_HOST='localhost')
        request = factory.get('/')
        request = self.generate_request(request)

        form = forms.Signup(data={
            'username': 'username2',
            'last_name': 'last_name',
            'first_name': 'first_name',
            'email': 'user@example.com',
            'password1': 'a779894c60365e80efdfe0f7172ebe2063e99e08',
            'password2': 'a779894c60365e80efdfe0f7172ebe2063e99e08'
        }, request=request)
        self.assertTrue(form.is_valid())

        session = form.confirmation()
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session_data = session_store(session_key=session.session_key)

        self.assertEqual(session_data.get('module'), 'django_tasker_account.forms')
        session_data['data']['session'] = session

        request = factory.get('/confirm/email/{session_key}/'.format(session_key=session.session_key))
        request = self.generate_request(request)

        response = views.confirm_email(request, data=session_data.get('data'))
        self.assertRedirects(
            response,
            '/',
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False,
        )

