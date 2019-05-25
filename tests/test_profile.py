from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.test import TestCase, override_settings, RequestFactory

from django_tasker_account import forms, views
from . import test_base


@override_settings(
    ALLOWED_HOSTS=['localhost'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class Profile(TestCase, test_base.Request):
    def setUp(self) -> None:
        User.objects.create_user(username='username', password='Qazwsx123', email='devnull@example.com')

    def test_forms(self):
        factory = RequestFactory(HTTP_HOST='localhost')
        request = factory.get('/accounts/login/')
        request = self.generate_request(request)
        request.user = get_object_or_404(User, username='username')

        form = forms.Profile(
            request=request,
            data={
                'last_name': 'Kazerogova',
                'first_name': 'Lilu',
                'gender': 1,
                'birth_date': '1981-01-01',
                'language': 'ru',
            }
        )
        self.assertTrue(form.is_valid())
        form.save()

        user = get_object_or_404(User, username='username')
        self.assertEqual(user.last_name, 'Kazerogova')
        self.assertEqual(user.first_name, 'Lilu')
        self.assertEqual(user.profile.gender, 1)
        self.assertEqual(str(user.profile.birth_date), '1981-01-01')
        self.assertEqual(user.profile.language, 'ru')

        self.assertEqual(user.profile.get_gender_display(), 'Male')

    def test_views(self):
        pass
