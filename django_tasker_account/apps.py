from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoTaskerAccountConfig(AppConfig):
    name = 'django_tasker_account'
    verbose_name = _("Django tasker account")
