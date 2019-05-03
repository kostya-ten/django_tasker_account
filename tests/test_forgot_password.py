from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, override_settings, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from django_tasker_account import forms


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
class ForgotPassword(TestCase, Request):
    def setUp(self) -> None:
        User.objects.create_user(username='username', email='user@example.com')

    def test_views(self):
        factory = RequestFactory(HTTP_HOST='localhost')
        request = factory.get('/')
        request = self.generate_request(request)

        form = forms.ForgotPassword(data={'email': 'user@example.com'}, request=request)
        self.assertTrue(form.is_valid())
        session = form.sendmail()

        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session_data = session_store(session_key=session.session_key)

        self.assertEqual(session_data.get('module'), 'django_tasker_account.forms')
        self.assertRegex(str(session_data.get('user_id')), '^[0-9]+$')
        self.assertEqual(session_data.get('next'), '/')
        self.assertRegex(session.session_key, '^[0-9a-z]+$')

