from django.contrib.auth.models import User
from django.test import TestCase, override_settings, RequestFactory
from django.core.exceptions import ValidationError

from . import validators, geobase, forms, models


class Validators(TestCase):

    def test_mobile_number(self):

        # Invalid
        with self.assertRaises(ValidationError):
            validators.mobile_number(74950000000)

        with self.assertRaises(ValidationError):
            validators.mobile_number('abc')

        # Valid
        self.assertEqual(validators.mobile_number(79090000000), '+79090000000')

    def test_username(self):

        # Invalid
        with self.assertRaises(ValidationError):
            validators.username('1kazerogova')

        with self.assertRaises(ValidationError):
            validators.username('!kazerogova')

        with self.assertRaises(ValidationError):
            validators.username('kaze-rog-ova')

        with self.assertRaises(ValidationError):
            validators.username('kaze-rog_ova')

        with self.assertRaises(ValidationError):
            validators.username('kaze rog ova')

        with self.assertRaises(ValidationError):
            validators.username('kazeogova!')

        with self.assertRaises(ValidationError):
            validators.username('kazeo.gova')

        with self.assertRaises(ValidationError):
            validators.username('kazeo@gova')

        # Valid
        self.assertEqual(validators.username('kazerogova'), 'kazerogova')
        self.assertEqual(validators.username('kazer-ogova'), 'kazer-ogova')
        self.assertEqual(validators.username('kazer_ogova'), 'kazer_ogova')
        self.assertEqual(validators.username('    kazer_ogova       '), 'kazer_ogova')
        self.assertEqual(validators.username('KAZEROGOVA'), 'kazerogova')

    def test_username_dublicate(self):
        User.objects.create_user(username='kazerogova')

        with self.assertRaises(ValidationError):
            validators.username_dublicate('kazerogova')

        validators.username_dublicate('kazerogova-lilu')

    def test_email(self):

        # Invalid
        with self.assertRaises(ValidationError):
            validators.email('kazerogova')

        with self.assertRaises(ValidationError):
            validators.email('kazerogova@')

        with self.assertRaises(ValidationError):
            validators.email('kazerogova@exampleexampleexampleexampleexampleexample.com')

        with self.assertRaises(ValidationError):
            validators.email('kazerogova@example.abc')

        with self.assertRaises(ValidationError):
            validators.email('kaze@rogova@example.com')

        # Valid
        self.assertEqual(validators.email('kazerogova@example.com'), 'kazerogova@example.com')
        self.assertEqual(validators.email('Kazerogova@example.com'), 'kazerogova@example.com')
        self.assertEqual(validators.email('        kazerogova@example.com        '), 'kazerogova@example.com')
        self.assertEqual(validators.email('kazerogova@yandex.com'), 'kazerogova@yandex.ru')
        self.assertEqual(validators.email('kazerogova@yandex.kz'), 'kazerogova@yandex.ru')
        self.assertEqual(validators.email('kazerogova@ya.ru'), 'kazerogova@yandex.ru')

    def test_email_dublicate(self):
        User.objects.create_user(username='kazerogova', email='kazerogova@example.com')

        # Invalid
        with self.assertRaises(ValidationError):
            validators.email_dublicate('kazerogova@example.com')

        with self.assertRaises(ValidationError):
            validators.email_dublicate('KAZEROGOVA@example.com')

        with self.assertRaises(ValidationError):
            validators.email_dublicate('         KAZEROGOVA@example.com          ')

        # Valid
        self.assertEqual(validators.email_dublicate('kazerogova@example.org'), 'kazerogova@example.org')


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class Geobase(TestCase):

    def test_geocoder(self):
        result = geobase.geocoder(query='Москва')
        self.assertEqual(result.country.en, 'Russia')
        self.assertEqual(result.province.en, 'Moscow')
        self.assertEqual(result.locality.en, 'Moscow')
        self.assertEqual(result.timezone.name, 'Europe/Moscow')
        self.assertEqual(result.latitude, 55.753215)
        self.assertEqual(result.longitude, 37.622504)

    def test_detect_ip(self):
        result = geobase.detect_ip(query='8.8.8.8')
        self.assertEqual(result.country.en, 'United States of America')
        self.assertEqual(result.province.en, 'District of Columbia')
        self.assertEqual(result.locality.en, 'City of Washington')
        self.assertEqual(result.timezone.name, 'America/New_York')
        self.assertEqual(result.latitude, 38.899513)
        self.assertEqual(result.longitude, -77.036527)

        result = geobase.detect_ip(query='2a02:6b8::feed:0ff')
        self.assertEqual(result.country.en, 'Russia')
        self.assertEqual(result.province.en, 'Moscow')
        self.assertEqual(result.locality.en, 'Moscow')
        self.assertEqual(result.timezone.name, 'Europe/Moscow')
        self.assertEqual(result.latitude, 55.755814)
        self.assertEqual(result.longitude, 37.617635)


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class Form(TestCase):
    def test_login(self):
        User.objects.create_user(username='username', password='Qazwsx123', email='devnull@example.com')

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

