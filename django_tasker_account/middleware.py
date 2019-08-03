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
            if request.user.profile.geobase:
                obj = request.user.profile.geobase.get_family()
                locality = obj.filter(type=4)
                if locality.exists():
                    timezone.activate(pytz.timezone(locality.last().timezone))
                else:
                    timezone.deactivate()

        response = self.get_response(request)
        return response
