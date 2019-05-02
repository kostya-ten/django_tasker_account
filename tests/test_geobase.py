import os

from django.test import TestCase, override_settings
from django_tasker_account import geobase


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
