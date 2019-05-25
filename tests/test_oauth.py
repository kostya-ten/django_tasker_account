from django.contrib.auth.models import User
from django.test import TestCase, override_settings, RequestFactory

from django_tasker_account import forms, views
from . import test_base


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class OAuth(TestCase, test_base.Request):
    def test_view(self):
        factory = RequestFactory(HTTP_HOST='localhost')

        request = factory.get('/accounts/oauth/google/')
        response = views.oauth_google(request)
        self.assertRegex(response.url, r'^https://accounts.google.com/o/oauth2/v2/auth')
        self.assertEqual(response.status_code, 302)

        request = factory.get('/accounts/oauth/yandex/')
        response = views.oauth_yandex(request)
        self.assertRegex(response.url, r'^https://oauth.yandex.ru/authorize')
        self.assertEqual(response.status_code, 302)

        request = factory.get('/accounts/oauth/mailru/')
        response = views.oauth_mailru(request)
        self.assertRegex(response.url, r'^https://oauth.mail.ru/login')
        self.assertEqual(response.status_code, 302)

        request = factory.get('/accounts/oauth/vk/')
        response = views.oauth_vk(request)
        self.assertRegex(response.url, r'^https:///oauth.vk.com/authorize')
        self.assertEqual(response.status_code, 302)

        request = factory.get('/accounts/oauth/facebook/')
        response = views.oauth_facebook(request)
        self.assertRegex(response.url, r'^https://www.facebook.com/v3.2/dialog/oauth')
        self.assertEqual(response.status_code, 302)
