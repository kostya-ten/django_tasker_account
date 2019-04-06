import phonenumbers
import re

from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from email_validator import validate_email, EmailNotValidError

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


def mobile_number(number):
    match = re.search(r'^[0-9]+$', str(number))
    if not match:
        raise ValidationError(_("Invalid mobile phone number"))

    number = "+{number}".format(number=number)
    result = carrier._is_mobile(number_type(phonenumbers.parse(number)))
    if not result:
        raise ValidationError(_('Invalid mobile phone number'))
    else:
        return number


def username(username):
    username = username.lower().strip()

    match = re.search(r'^[a-z]+[a-z0-9]+[_-]?[a-z0-9]+$', username)
    if match:
        return username
    else:
        message = "Enter a valid username. This value may contain only English letters, numbers, and _ - characters." \
                  "Username should not begin with a number."
        raise ValidationError(_(message))


def username_dublicate(username):
    username = username.lower().strip()

    user = User.objects.filter(username=username)
    if user.count():
        raise ValidationError(_("A user with that username already exists."))

    return username


def email(email):
    email = email.lower().strip()

    user = email.rsplit('@', 1)[0]
    domain = email.rsplit('@', 1)[-1]
    if domain == 'ya.ru' or domain == 'yandex.by' or domain == 'yandex.com' or domain == 'yandex.kz' or domain == 'yandex.ua':
        email = user+'@yandex.ru'

    try:
        validate_email(email)
    except EmailNotValidError:
        raise ValidationError(_("Enter a valid email address."))

    return email


def email_dublicate(email):
    email = email.lower().strip()

    user = email.rsplit('@', 1)[0]
    domain = email.rsplit('@', 1)[-1]
    if domain == 'ya.ru' or domain == 'yandex.by' or domain == 'yandex.com' or domain == 'yandex.kz' or domain == 'yandex.ua':
        email = user+'@yandex.ru'

    if User.objects.filter(email=email).count():
        raise ValidationError(_("User with this email is already exists."))

    return email
