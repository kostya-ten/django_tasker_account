from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Testing'

    def handle(self, *args, **options):
        pass