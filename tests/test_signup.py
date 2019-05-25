from django.contrib.auth.models import User
from django.test import TestCase, override_settings, RequestFactory
from django.core import mail
from django.urls import reverse

from django_tasker_account import forms, views, converters
from . import test_base


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class Signup(TestCase, test_base.Request):
    def setUp(self) -> None:
        psw = 'Qazwsx123'
        User.objects.create_user(username='username', password=psw, email='devnull@example.com')

    def test_forms(self):
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

    def test_views(self):
        factory = RequestFactory(HTTP_HOST='localhost')
        request = factory.post(reverse('django_tasker_account:signup'), data={
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
            reverse('django_tasker_account:login'),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False,
        )
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox.pop()
        self.assertEqual(message.subject, 'Please confirm email address')
        self.assertEqual(message.to.pop(), 'user2@example.com')

    def test_views_confirm_email(self):
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
        confirm_email = converters.ConfirmEmail().to_python(session_key=session.session_key)

        self.assertEqual(confirm_email.module, 'django_tasker_account.forms')

        request = factory.get('/confirm/email/{session_key}/'.format(session_key=session.session_key))
        request = self.generate_request(request)
        response = views.confirm_email(request, data=confirm_email)

        self.assertRedirects(
            response,
            '/',
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False,
        )

        user = User.objects.get(username='username2')
        self.assertEqual(user.username, 'username2')
        self.assertEqual(user.last_name, 'last_name')
        self.assertEqual(user.first_name, 'first_name')
        self.assertEqual(user.email, 'user@example.com')
        self.assertEqual(user.profile.language, 'en')
