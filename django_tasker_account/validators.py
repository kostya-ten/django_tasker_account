import phonenumbers
import re

from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from email_validator import validate_email, EmailNotValidError

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


def mobile_number(number: int) -> str:
    """
    Checks the validity of a mobile phone number.

    :param number: mobile phone number.
    :returns: number
    :raise: ValidationError If the mobile phone number is not valid
    """

    match = re.search(r'^[0-9]+$', str(number))
    if not match:
        raise ValidationError(_("Invalid mobile phone number"))

    number = "+{number}".format(number=number)
    result = carrier._is_mobile(number_type(phonenumbers.parse(number)))
    if not result:
        raise ValidationError(_('Invalid mobile phone number'))
    else:
        return number


def username(username: str) -> str:
    """
    Checks the validity of an username.

    :param username: User name сhecked.
    :returns: username
    :raise: ValidationError If the username is not a regular expression ^[a-z]+[a-z0-9]+[_-]?[a-z0-9]+$
    """
    username = username.lower().strip()

    match = re.search(r'^[a-z]+[a-z0-9]+[_-]?[a-z0-9]+$', username)
    if match:
        return username
    else:
        message = "Enter a valid username. This value may contain only English letters, numbers, and _ - characters." \
                  "Username should not begin with a number."
        raise ValidationError(_(message))


def username_dublicate(username: str) -> str:
    """
    Checks the dublicate an username.

    :param username: User name сhecked.
    :returns: username
    :raise: ValidationError If the username is dublicate
    """

    username = username.lower().strip()

    user = User.objects.filter(username=username)
    if user.count():
        raise ValidationError(_("A user with that username already exists."))

    return username


def email(email: str) -> str:
    """
    Checks the validity syntax of an email

    :param email: email address
    :returns: email
    :raise: ValidationError If the incorrect email address
    """
    email = email.lower().strip()

    user = email.rsplit('@', 1)[0]
    domain = email.rsplit('@', 1)[-1]
    if domain == 'ya.ru'\
            or domain == 'yandex.by'\
            or domain == 'yandex.com'\
            or domain == 'yandex.kz'\
            or domain == 'yandex.ua':
        email = user+'@yandex.ru'

    try:
        validate_email(email)
    except EmailNotValidError:
        raise ValidationError(_("Enter a valid email address."))

    return email


def email_dublicate(email: str) -> str:
    """
    Checks the dublicate an email

    :param email: email address
    :returns: email
    :raise: ValidationError If the email address is dublicate
    """
    email = email.lower().strip()

    user = email.rsplit('@', 1)[0]
    domain = email.rsplit('@', 1)[-1]
    if domain == 'ya.ru'\
            or domain == 'yandex.by'\
            or domain == 'yandex.com'\
            or domain == 'yandex.kz'\
            or domain == 'yandex.ua':
        email = user+'@yandex.ru'

    if User.objects.filter(email=email).exists():
        raise ValidationError(_("User with this email is already exists."))

    return email


def email_exists(email: str) -> str:
    """
    Checks the not exists an email

    :param email: email address
    :returns: email
    :raise: ValidationError If the email address is not exists
    """
    email = email.lower().strip()

    user = email.rsplit('@', 1)[0]
    domain = email.rsplit('@', 1)[-1]
    if domain == 'ya.ru'\
            or domain == 'yandex.by'\
            or domain == 'yandex.com'\
            or domain == 'yandex.kz'\
            or domain == 'yandex.ua':
        email = user+'@yandex.ru'

    if not User.objects.filter(email=email).exists():
        raise ValidationError(_("User with this email is not exists"))

    return email


def email_blacklist(email: str) -> str:
    """
    Checks the blacklist db an email

    :param email: email address
    :returns: email
    :raise: ValidationError If the email address is blacklist db
    """
    email = email.lower().strip()
    domain = email.rsplit('@', 1)[-1]
    if domain == 'for4mail.com'\
            or domain == '2mailnext.com'\
            or domain == 'prmail.top'\
            or domain == 'youmails.online'\
            or domain == 'reddcoin2.com'\
            or domain == 'proto2mail.com'\
            or domain == 'mail-2-you.com'\
            or domain == 'for4mail.com'\
            or domain == '2mailnext.top'\
            or domain == 'jo-mail.com'\
            or domain == 'mailapps.online'\
            or domain == 'plutocow.com'\
            or domain == 'ezehe.com'\
            or domain == 'sharklasers.com'\
            or domain == 'guerrillamail.info'\
            or domain == 'grr.la'\
            or domain == 'guerrillamail.biz'\
            or domain == 'guerrillamail.com'\
            or domain == 'guerrillamail.de'\
            or domain == 'guerrillamail.net'\
            or domain == 'guerrillamail.org'\
            or domain == 'guerrillamailblock.com'\
            or domain == 'pokemail.net'\
            or domain == 'spam4.me'\
            or domain == 'fosil.pro'\
            or domain == 'socrazy.club'\
            or domain == 'getamailbox.org'\
            or domain == 'ourawesome.life' \
            or domain == 'mailboxonline.org' \
            or domain == 'careless-whisper.com' \
            or domain == 'ourawesome.life' \
            or domain == 'ourawesome.online' \
            or domain == 'secure-box.info' \
            or domain == 'secure-box.online' \
            or domain == 'socrazy.club' \
            or domain == 'socrazy.online' \
            or domain == 'yevme.com' \
            or domain == 'trashmail.com' \
            or domain == '0box.eu' \
            or domain == 'contbay.com' \
            or domain == 'damnthespam.com' \
            or domain == 'kurzepost.de' \
            or domain == 'objectmail.com' \
            or domain == 'proxymail.eu' \
            or domain == 'rcpt.at' \
            or domain == 'trash-mail.at' \
            or domain == 'trashmail.at' \
            or domain == 'trashmail.com' \
            or domain == 'trashmail.io' \
            or domain == 'trashmail.me' \
            or domain == 'trashmail.net' \
            or domain == 'wegwerfmail.de' \
            or domain == 'wegwerfmail.net' \
            or domain == 'wegwerfmail.org':
        raise ValidationError(_("Email address cannot be registered!"))
    return email


def password(password: str) -> str:
    """
    Checks the password syntax

    :param password: password
    :returns: password
    :raise: ValidationError If the password is not correct
    """
    match = re.search(r'^[a-z0-9`@#$%^&*()_=+\[\]{};:"\\|.,]+$', password, re.IGNORECASE)
    if not match:
        err = _('For the password, you can use only Latin letters, numbers, and symbols')
        raise ValidationError(err)

    return password
