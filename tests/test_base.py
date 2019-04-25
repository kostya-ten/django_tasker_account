import os

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, override_settings, RequestFactory
from django.core.exceptions import ValidationError
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail

from django_tasker_account import validators, geobase, forms, views


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

    def test_email_blacklist(self):
        with self.assertRaises(ValidationError):
            validators.email_blacklist('example@2mailnext.com')

    def test_password(self):
        with self.assertRaises(ValidationError):
            validators.password('嗨')

        self.assertEqual(validators.password('password'), 'password')
        self.assertEqual(validators.password('pass#word'), 'pass#word')
        self.assertEqual(validators.password('`@#$%^&*()_=+\[\]{};:"\\|.,'), '`@#$%^&*()_=+\[\]{};:"\\|.,')


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class Geobase(TestCase):

    def test_geocoder(self):
        result = geobase.detect_geo(query='Москва')
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

        if not os.environ.get('TRAVIS'):
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
class Form(TestCase, Request):
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

    def test_signup(self):
        User.objects.create_user(username='username', password='Qazwsx123', email='devnull@example.com')

        # Correct data
        form = forms.Signup(data={
            'username': 'username2',
            'last_name': 'Kazerogova',
            'first_name': 'Lilu',
            'email': 'kazerogova@example.com',
            'password1': 'na0tKtKdHY',
            'password2': 'na0tKtKdHY',
        })
        self.assertTrue(form.is_valid())

        # Incorrect data
        form = forms.Signup(data={})
        self.assertTrue(form.has_error('username'))
        self.assertTrue(form.has_error('last_name'))
        self.assertTrue(form.has_error('first_name'))
        self.assertTrue(form.has_error('email'))
        self.assertTrue(form.has_error('password1'))
        self.assertTrue(form.has_error('password2'))
        self.assertFalse(form.is_valid())

        form = forms.Signup(data={'username': 'username'})
        self.assertTrue(form.has_error('username'))

        form = forms.Signup(data={'username': 'username2'})
        self.assertTrue(form.has_error('last_name'))

        form = forms.Signup(data={'username': 'username2', 'last_name': 'last_name'})
        self.assertTrue(form.has_error('first_name'))

        form = forms.Signup(data={'username': 'username2', 'last_name': 'last_name', 'first_name': 'first_name'})
        self.assertTrue(form.has_error('email'))

        form = forms.Signup(data={
            'username': 'username2',
            'last_name': 'last_name',
            'first_name': 'first_name',
            'email': 'user@fdsfsdfadsasdfgsdbfgnxgnxfgnhxg.vom'
        })
        self.assertTrue(form.has_error('email'))

        form = forms.Signup(data={
            'username': 'username2',
            'last_name': 'last_name',
            'first_name': 'first_name',
            'email': 'fdsfsdfadsasdfgsdbfgnxgnxfgnhxg.vom'
        })
        self.assertTrue(form.has_error('email'))

        form = forms.Signup(data={
            'username': 'username2',
            'last_name': 'last_name',
            'first_name': 'first_name',
            'email': 'devnull@example.com'
        })
        self.assertTrue(form.has_error('email'))

        form = forms.Signup(data={
            'username': 'username2',
            'last_name': 'last_name',
            'first_name': 'first_name',
            'email': 'гыук@example.com'
        })
        self.assertTrue(form.has_error('password1'))

        form = forms.Signup(data={
            'username': 'username2',
            'last_name': 'last_name',
            'first_name': 'first_name',
            'email': 'user@example.com',
            'password1': 'тест'
        })
        self.assertTrue(form.has_error('password1'))

        form = forms.Signup(data={
            'username': 'username2',
            'last_name': 'last_name',
            'first_name': 'first_name',
            'email': 'user@example.com',
            'password1': 'a779894c60365e80efdfe0f7172ebe2063e99e09'
        })
        self.assertTrue(form.has_error('password2'))

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
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox.pop()
        self.assertEqual(message.subject, 'Please confirm email address')
        self.assertEqual(message.to.pop(), 'user@example.com')
        self.assertInHTML(
            '<a href="https://localhost/accounts/confirm/email/{session_key}/">'.format(
                session_key=session.session_key) + 'https://localhost/accounts/confirm/email/{session_key}/</a>'.format(
                session_key=session.session_key
            ),
            message.body)

        request = factory.post('/accounts/signup/', data={
            'username': 'username3',
            'last_name': 'last_name',
            'first_name': 'first_name',
            'email': 'user2@example.com',
            'password1': 'a779894c60365e80efdfe0f7172ebe2063e99e08',
            'password2': 'a779894c60365e80efdfe0f7172ebe2063e99e08'
        })
        request = self.generate_request(request)

        response = views.signup(request)
        self.assertRedirects(
            response,
            '/accounts/login/',
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False,
        )
