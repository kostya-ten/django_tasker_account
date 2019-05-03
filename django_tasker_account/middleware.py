import pytz
from django.utils import timezone, translation


# Change language
class Language:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.profile.language:
                translation.activate(request.user.profile.language)

        response = self.get_response(request)
        return response


# Change timezone
class Timezone:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.profile.geobase and request.user.profile.geobase.timezone.name:
                timezone.activate(pytz.timezone(request.user.profile.geobase.timezone.name))
            else:
                timezone.deactivate()

        response = self.get_response(request)
        return response
