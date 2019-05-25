import hashlib
from datetime import datetime, timezone, timedelta
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings, RequestFactory
from django.urls import reverse

from django_tasker_account import views, converters
from . import test_base


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class OAuth(TestCase, test_base.Request):
    def test_view(self):
        factory = RequestFactory(HTTP_HOST='localhost')

        request = factory.get(reverse('django_tasker_account:oauth_google'))
        response = views.oauth_google(request)
        self.assertRegex(response.url, r'^https://accounts.google.com/o/oauth2/v2/auth')
        self.assertEqual(response.status_code, 302)

        request = factory.get(reverse('django_tasker_account:oauth_yandex'))
        response = views.oauth_yandex(request)
        self.assertRegex(response.url, r'^https://oauth.yandex.ru/authorize')
        self.assertEqual(response.status_code, 302)

        request = factory.get(reverse('django_tasker_account:oauth_mailru'))
        response = views.oauth_mailru(request)
        self.assertRegex(response.url, r'^https://oauth.mail.ru/login')
        self.assertEqual(response.status_code, 302)

        request = factory.get(reverse('django_tasker_account:oauth_vk'))
        response = views.oauth_vk(request)
        self.assertRegex(response.url, r'^https:///oauth.vk.com/authorize')
        self.assertEqual(response.status_code, 302)

        request = factory.get(reverse('django_tasker_account:oauth_facebook'))
        response = views.oauth_facebook(request)
        self.assertRegex(response.url, r'^https://www.facebook.com/v3.2/dialog/oauth')
        self.assertEqual(response.status_code, 302)

        # Completion
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store()

        m = hashlib.sha256()
        m.update("test_id".encode("utf-8"))

        dt = datetime.now(timezone.utc) + timedelta(seconds=60*60*24)

        session["oauth"] = {
            'provider': 1,
            'id': m.hexdigest(),
            'access_token': 'access_token',
            'birth_date': '1981-01-01',
            'last_name': 'Казерогова',
            'first_name': 'Лилу',
            'expires_in': dt.isoformat(),
            'module': 'django_tasker_account.views',
            'next': '/',
            'username': 'kazerogova',
            'email': 'devnull@yandex-team.ru',
            'gender': 1,
            'avatar': None,
        }
        session.create()

        url = reverse('django_tasker_account:oauth_completion', kwargs={'data': session.session_key})
        obj = converters.OAuth().to_python(session_key=session.session_key)

        request = factory.get(url)
        request = self.generate_request(request)
        response = views.oauth_completion(request, data=obj)
        self.assertTrue(response.status_code, 302)

        user = User.objects.filter(username="kazerogova")
        self.assertTrue(user.exists())

