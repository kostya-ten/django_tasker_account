from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings, RequestFactory

from django_tasker_account import forms, views, converters
from . import test_base


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class ForgotPassword(TestCase, test_base.Request):
    def setUp(self) -> None:
        User.objects.create_user(username='username', email='user@example.com')

    def test_forms(self):
        factory = RequestFactory(HTTP_HOST='localhost')
        request = factory.get('/')
        request = self.generate_request(request)

        form = forms.ForgotPassword(data={'email': 'user@example.com'}, request=request)
        self.assertTrue(form.is_valid())
        session = form.sendmail()

        obj = converters.ChangePassword().to_python(session_key=session.session_key)

        self.assertEqual(obj.module, 'django_tasker_account.forms')
        self.assertRegex(str(obj.user_id), '^[0-9]+$')
        self.assertEqual(obj.next, '/')
        self.assertRegex(obj.session.session_key, '^[0-9a-z]+$')

    def test_views(self):
        factory = RequestFactory(HTTP_HOST='localhost')
        request = factory.get('/accounts/forgot_password/')
        request = self.generate_request(request)

        response = views.forgot_password(request)
        self.assertEqual(response.status_code, 200)

        # Not found email
        request = factory.post('/accounts/forgot_password/', {'email': 'notfound@example.com'})
        request = self.generate_request(request)
        response = views.forgot_password(request)
        self.assertEqual(response.status_code, 400)

        request = factory.post('/accounts/forgot_password/', {'email': 'user@example.com'})
        request = self.generate_request(request)
        response = views.forgot_password(request)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox.pop()
        self.assertEqual(message.subject, 'Password recovery')
        self.assertEqual(message.to.pop(), 'user@example.com')

        self.assertRegex(message.body, '/accounts/change/password/')

        # change_password
        request = factory.post('/accounts/forgot_password/', {'email': 'user@example.com'})
        request = self.generate_request(request)
        form = forms.ForgotPassword(data=request.POST, request=request)
        self.assertTrue(form.is_valid())

        session = form.sendmail()
        obj = converters.ChangePassword().to_python(session_key=session.session_key)
        self.assertEqual(obj.module, 'django_tasker_account.forms')
        self.assertRegex(str(obj.user_id), r'^[0-9]+$')

        request = factory.get('change/password/{session_key}/'.format(session_key=session.session_key))
        request = self.generate_request(request)
        response = views.change_password(request, data=obj)
        self.assertTrue(response.status_code, 200)

        request = factory.post(
            'change/password/{session_key}/'.format(session_key=session.session_key),
            {'new_password1': 'NDMLR2OSwQ', 'new_password2': 'NDMLR2OSwQ'}
        )
        request = self.generate_request(request)
        response = views.change_password(request, data=obj)
        self.assertTrue(response.status_code, 302)

        user = User.objects.get(username='username')
        self.assertTrue(user.check_password('NDMLR2OSwQ'))
