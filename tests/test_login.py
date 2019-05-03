from django.contrib.auth.models import User
from django.test import TestCase, override_settings, RequestFactory

from django_tasker_account import forms, views
from . import test_base


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class Login(TestCase, test_base.Request):
    def setUp(self) -> None:
        User.objects.create_user(username='username', password='Qazwsx123', email='devnull@example.com')

    def test_forms(self):
        # Correct data
        form = forms.Login(data={'username': 'username', 'password': 'Qazwsx123'})
        self.assertTrue(form.is_valid())

        form = forms.Login(data={'username': 'USERNAME', 'password': 'Qazwsx123'})
        self.assertTrue(form.is_valid())

        form = forms.Login(data={'username': '   USERNAME   ', 'password': '   Qazwsx123   '})
        self.assertTrue(form.is_valid())

        form = forms.Login(data={'username': 'devnull@example.com', 'password': 'Qazwsx123'})
        self.assertTrue(form.is_valid())

        # Incorrect data
        form = forms.Login(data={'username': 'username', 'password': 'IncorrectPassword'})
        self.assertFalse(form.is_valid())

        form = forms.Login(data={'username': 'IncorrectUsername', 'password': 'Qazwsx123'})
        self.assertFalse(form.is_valid())

        # HTTP correct testing
        factory = RequestFactory(HTTP_HOST='localhost')
        request = factory.post('/accounts/login/')

        form = forms.Login(data={'username': 'username', 'password': 'Qazwsx123'}, request=request)
        self.assertTrue(form.is_valid())

        form = forms.Login(data={'username': 'USERNAME', 'password': 'Qazwsx123'}, request=request)
        self.assertTrue(form.is_valid())

        form = forms.Login(data={'username': '   USERNAME   ', 'password': '   Qazwsx123   '}, request=request)
        self.assertTrue(form.is_valid())

        form = forms.Login(data={'username': 'devnull@example.com', 'password': 'Qazwsx123'}, request=request)
        self.assertTrue(form.is_valid())

        # HTTP incorrect testing
        factory = RequestFactory(HTTP_HOST='localhost')
        request = factory.post('/accounts/login/')

        form = forms.Login(data={'username': 'username', 'password': 'IncorrectPassword'}, request=request)
        self.assertFalse(form.is_valid())

        form = forms.Login(data={'username': 'IncorrectUsername', 'password': 'Qazwsx123'}, request=request)
        self.assertFalse(form.is_valid())

    def test_view(self):
        factory = RequestFactory(HTTP_HOST='localhost')

        # View login correct
        request = factory.get('/accounts/login/')
        response = views.login(request)
        self.assertEqual(response.status_code, 200)

        request = factory.post('/accounts/login/', {'username': 'username', 'password': 'Qazwsx123'})
        request = self.generate_request(request)
        response = views.login(request)
        self.assertEqual(response.status_code, 302)

        request = factory.post('/accounts/login/', {'username': 'USERNAME', 'password': 'Qazwsx123'})
        request = self.generate_request(request)
        response = views.login(request)
        self.assertEqual(response.status_code, 302)

        request = factory.post('/accounts/login/', {'username': '   USERNAME   ', 'password': '   Qazwsx123   '})
        request = self.generate_request(request)
        response = views.login(request)
        self.assertEqual(response.status_code, 302)

        request = factory.post('/accounts/login/', {'username': 'devnull@example.com', 'password': 'Qazwsx123'})
        request = self.generate_request(request)
        response = views.login(request)
        self.assertEqual(response.status_code, 302)

        # View login incorrect
        request = factory.post('/accounts/login/', {'username': 'username', 'password': 'Qazwsx124'})
        request = self.generate_request(request)
        response = views.login(request)
        self.assertEqual(response.status_code, 400)
