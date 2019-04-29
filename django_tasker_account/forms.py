import logging
import re
from email.utils import make_msgid, formataddr
from importlib import import_module

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.forms import TextInput, PasswordInput
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from . import validators
logger = logging.getLogger('tasker_account')


class Login(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'username',
                'placeholder': _('Username')
            }
        )
    )

    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'current-password',
                'placeholder': _('Password')
            }
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


class Signup(UserCreationForm):
    username = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('Username')
            }
        ),
        validators=[
            validators.username,
            validators.username_dublicate,
        ]
    )

    last_name = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('Last name')
            }
        )
    )

    first_name = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('First name')
            }
        )
    )

    email = forms.EmailField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('Email')
            }
        ),
        validators=[
            validators.email,
            validators.email_blacklist,
            validators.email_dublicate,
        ]
    )

    password1 = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'new-password',
                'placeholder': _('Password')}
        ),
        validators=[
            validators.password
        ]
    )

    password2 = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'new-password',
                'placeholder': _('Confirm password')
            }
        ),
        validators=[
            validators.password
        ]
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        return self.cleaned_data.get('username').lower().strip()

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()

        user = email.rsplit('@', 1)[0]
        domain = email.rsplit('@', 1)[-1]
        if domain == 'ya.ru'\
                or domain == 'yandex.by'\
                or domain == 'yandex.com'\
                or domain == 'yandex.kz'\
                or domain == 'yandex.ua':
            email = user+'@yandex.ru'
        return email

    def clean_password1(self):
        return self.cleaned_data.get('password1').strip()

    def confirmation(self) -> import_module(settings.SESSION_ENGINE).SessionStore:
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store()

        session['data'] = self.cleaned_data
        session['module'] = __name__

        if hasattr(self.request, 'GET'):
            session['data']['next'] = self.request.GET.get('next', '/')
        else:
            session['data']['next'] = '/'

        session.create()

        subject = render_to_string('django_tasker_account/email/signup.subject.txt', {}).strip()
        body = render_to_string('django_tasker_account/email/signup.body.html', {
            'session_key': session.session_key,
            'host': self.request.get_host()
        })

        if hasattr(self.request, 'get_host'):
            headers = {'Message-ID': make_msgid(domain=self.request.get_host())}
        else:
            headers = {'Message-ID': make_msgid(domain='localhost')}

        name_email = getattr(settings, 'EMAIL_NAME', settings.DEFAULT_FROM_EMAIL)
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=formataddr((name_email, settings.DEFAULT_FROM_EMAIL)),
            to=[self.cleaned_data.get('email')],
            headers=headers,
        )
        msg.content_subtype = "html"
        msg.send()

        logger.debug("Confirmation code: {session}".format(session=session.session_key))
        return session

    #def save(self):
    #    return super().save(commit=True)

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'email', 'password1', 'password2')


class ForgotPassword(PasswordResetForm):
    email = forms.EmailField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'placeholder': _('Email')
            }),
        validators=[
            validators.email,
            validators.email_exists,
        ]
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def send_mail(self) -> import_module(settings.SESSION_ENGINE).SessionStore:
        session_store = import_module(settings.SESSION_ENGINE).SessionStore

        user = get_object_or_404(User, email=self.cleaned_data.get('email'))

        session = session_store()
        session['user_id'] = user.id
        session['next'] = self.request.GET.get('next')
        session['module'] = __name__
        session.create()

    #     subject = render_to_string('accounts/email/forgot_password.subject.txt', {}).strip()
    #     body = render_to_string('accounts/email/forgot_password.body.html', {
    #         'session_key': session.session_key,
    #         'host': self.request.get_host()
    #     })
    #
    #     headers = {'Message-ID': make_msgid(domain=self.request.get_host())}
    #     msg = EmailMessage(
    #         subject=subject,
    #         body=body,
    #         from_email=formataddr((settings.EMAIL_NAME, settings.DEFAULT_FROM_EMAIL)),
    #         to=[self.cleaned_data.get('email')],
    #         headers=headers
    #     )
    #     msg.content_subtype = "html"
    #     msg.send()
    #     return session
    #
    # def user(self):
    #     return User.objects.filter(email=self.cleaned_data.get('email'))
    #
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     email = email.lower().strip()
    #     return email