from django.core.management.base import BaseCommand
from django_tasker_account import geobase
from ipaddress import ip_address


class Command(BaseCommand):
    help = 'Geobase'

    def add_arguments(self, parser):
        parser.add_argument('--action', nargs='+', default='ip', type=str)
        parser.add_argument('ip', nargs='?', type=str)

    def handle(self, *args, **options):
        if options.get('action') == 'ip':
            ip = ip_address(options.get('ip'))
            if ip.is_global:
                result = geobase.detect_ip(options.get('ip'))
                print("Country:{country}".format(country=result.country.en))
                print("Province:{province}".format(province=result.province.en))
                print("Locality:{locality}".format(locality=result.locality.en))
                print("Timezone:{timezone}".format(timezone=result.timezone))
                print("Coordinates:{latitude} {longitude}".format(latitude=result.latitude, longitude=result.longitude))
                print("Link map yandex:https://yandex.ru/maps/?ll={longitude},{latitude}&z=15".format(
                    latitude=result.latitude,
                    longitude=result.longitude,
                ))
                print("Link map google:https://www.google.ru/maps/@{latitude},{longitude},14z?hl=ru".format(
                    latitude=result.latitude,
                    longitude=result.longitude,
                ))
