import re
from os import urandom
from pathlib import Path

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _, get_supported_language_variant
from django.db import models
from django.contrib.auth.models import User

from . import validators


class GeobaseCountry(models.Model):
    ru = models.CharField(max_length=255, verbose_name=_("Name russian"), db_index=True)
    en = models.CharField(max_length=255, verbose_name=_("Name english"), db_index=True)

    def __str__(self):
        return '{en}, {ru}'.format(ru=self.ru, en=self.en)

    class Meta:
        verbose_name = _("Geobase сountry")
        verbose_name_plural = _("Geobase сountry")
        unique_together = (("ru", "en"),)


class GeobaseProvince(models.Model):
    ru = models.CharField(max_length=255, verbose_name=_("Name russian"), db_index=True)
    en = models.CharField(max_length=255, verbose_name=_("Name english"), db_index=True)

    def __str__(self):
        return '{en}, {ru}'.format(ru=self.ru, en=self.en)

    class Meta:
        verbose_name = _("Geobase province")
        verbose_name_plural = _("Geobase province")
        unique_together = (("ru", "en"),)


class GeobaseLocality(models.Model):
    ru = models.CharField(max_length=255, verbose_name=_("Name russian"), db_index=True)
    en = models.CharField(max_length=255, verbose_name=_("Name english"), db_index=True)

    def __str__(self):
        return '{en}, {ru}'.format(ru=self.ru, en=self.en)

    class Meta:
        verbose_name = _("Geobase locality")
        verbose_name_plural = _("Geobase locality")
        unique_together = (("ru", "en"),)


class GeobaseTimezone(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Time zone"))

    def __str__(self):
        return '{name}'.format(name=self.name)

    class Meta:
        verbose_name = _("Geobase timezone")
        verbose_name_plural = _("Geobase timezone")
        unique_together = ("name",)


class Geobase(models.Model):
    country = models.ForeignKey(GeobaseCountry, on_delete=models.CASCADE, verbose_name=_("Country"))
    province = models.ForeignKey(GeobaseProvince, on_delete=models.CASCADE, null=True, verbose_name=_("Province"))
    locality = models.ForeignKey(GeobaseLocality, on_delete=models.CASCADE, verbose_name=_("Locality"))
    timezone = models.ForeignKey(GeobaseTimezone, on_delete=models.CASCADE, verbose_name=_("Time zone"))
    latitude = models.FloatField(verbose_name=_("Latitude"))
    longitude = models.FloatField(verbose_name=_("Longitude"))

    class Meta:
        verbose_name = _("Geobase")
        verbose_name_plural = _("Geobase")
        unique_together = (('country', 'province', 'locality'),)

    def __str__(self):
        return "{country}, {province}, {locality}".format(
            country=self.country,
            province=self.province,
            locality=self.locality,
        )


class Profile(models.Model):

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
        choices=settings.LANGUAGES,
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

    geobase = models.ForeignKey(
        Geobase,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Geobase")
    )

    def path(instance, filename):
        extension = Path(filename).suffix
        key = urandom(16).hex()
        result = re.match(r'([a-z0-9]{2})([a-z0-9]{2})', key)
        return 'avatar/{0}/{1}/{2}'.format(result.group(1), result.group(2), key + extension)

    avatar = models.ImageField(upload_to=path, null=True, blank=True)

    def __str__(self):
        return 'User profile {user}'.format(user=self.user)


class Oauth(models.Model):
    PROVIDER = (
        (1, 'Google'),
        (2, 'Yandex'),
        (3, 'Mail.ru'),
        (4, 'VK.com'),
        (5, 'Facebook'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    oauth_id = models.CharField(max_length=255, verbose_name=_("Oauth ID"))
    provider = models.IntegerField(choices=PROVIDER, verbose_name=_("Server"))

    access_token = models.CharField(max_length=255, verbose_name=_("Access token"))
    expires_in = models.DateTimeField(verbose_name=_("Expires date"))

    class Meta:
        unique_together = (('oauth_id', 'provider'),)
        verbose_name = _("OAuth")
        verbose_name_plural = _("OAuth")

    def __str__(self):
        return '%s %s' % (self.provider, self.user)

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
