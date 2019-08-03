from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoTaskerAccountConfig(AppConfig):
    name = 'django_tasker_account'
    verbose_name = _("Tasker account")

    def ready(self):
        if not self.apps.is_installed('django_tasker_geobase'):
            raise Exception("Add in settings.py to section INSTALLED_APPS application django_tasker_geobase")
