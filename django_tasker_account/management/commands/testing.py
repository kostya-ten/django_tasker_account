import base64
import hashlib
import hmac
import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Testing'

    def handle(self, *args, **options):
        pass
