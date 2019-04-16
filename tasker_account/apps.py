from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TaskerAccountConfig(AppConfig):
    name = 'tasker_account'
    verbose_name = _("Tasker account")
