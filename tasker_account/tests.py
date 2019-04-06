from django.contrib.auth.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError

from . import validators


class Validators(TestCase):

    def test_validate_mobile_number(self):

        # Invalid
        with self.assertRaises(ValidationError):
            validators.mobile_number('74950000000')

        with self.assertRaises(ValidationError):
            validators.mobile_number('abc')

        # Valid
        self.assertEqual(validators.mobile_number('79090000000'), '+79090000000')

    def test_validate_username(self):

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

    def test_validate_username_dublicate(self):
        User.objects.create_user(username='kazerogova')

        with self.assertRaises(ValidationError):
            validators.username_dublicate('kazerogova')

        validators.username_dublicate('kazerogova-lilu')

    def test_validate_email(self):

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

    def test_validate_email_dublicate(self):
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

