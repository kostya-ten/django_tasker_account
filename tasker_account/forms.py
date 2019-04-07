import logging
import re

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import TextInput, PasswordInput
from django.contrib import auth
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger('tasker_account')


class Login(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(
            attrs={'class': 'form-control', 'autocomplete': 'username', 'placeholder': _('Username')}
        )
    )

    password = forms.CharField(
        widget=PasswordInput(
            attrs={'class': 'form-control', 'autocomplete': 'current-password', 'placeholder': _('Password')}
        )
    )

    remember = forms.BooleanField(required=False)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        username = username.lower().strip()

        if re.search(r'@', username):
            user = User.objects.filter(email=username)
            if user.count():
                return user.last().username

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        password = password.strip()
        return password

    def login(self) -> User:
        """
        User authorization
        """
        if self.data.get('remember'):
            self.request.session.set_expiry(getattr(settings, 'SESSION_COOKIE_AGE'))

        user = self.get_user()
        auth.login(self.request, user)

        logger.info("User authentication username:{username}, remember:{remember}".format(
            username=user.username,
            remember=self.data.get('remember', 'off'),
        ))
        return user
