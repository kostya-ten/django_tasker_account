from os import urandom
from pathlib import Path

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _, get_supported_language_variant
from django.db import models
from django.contrib.auth.models import User

from . import validators


class Profile(models.Model):
    LANGUAGES = [
        ('en-US', 'English'),
        ('ru-RU', 'Русский'),
    ]

    GENDER = [
        (1, _('Male')),
        (2, _('Female')),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )

    language = models.CharField(
        max_length=5,
        choices=LANGUAGES,
        verbose_name=_("Language"),
        default=get_supported_language_variant(getattr(settings, 'LANGUAGE_CODE', 'en-US'), strict=False)
    )

    gender = models.SmallIntegerField(
        choices=GENDER,
        null=True,
        blank=True,
        verbose_name=_("Gender")
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Birth date")
    )

    phone = models.BigIntegerField(
        null=True,
        blank=True,
        validators=[validators.mobile_number]
    )

    def path(instance, filename):
        extension = Path(filename).suffix
        return 'avatar/{0}/{1}/{2}'.format(urandom(1).hex(), urandom(1).hex(), urandom(16).hex() + extension)

    avatar = models.ImageField(upload_to=path, null=True, blank=True)

    def __str__(self):
        return 'User profile {user}'.format(user=self.user)


# Signals
@receiver(post_save, sender=User)
def account_profile(instance=None, created=None, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        profile = Profile.objects.filter(user=instance)
        if not profile.count():
            Profile.objects.create(user=instance)

    instance.profile.save()
