import logging
import re
from email.utils import make_msgid, formataddr
from importlib import import_module

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, PasswordChangeForm, \
    SetPasswordForm
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.forms import TextInput, PasswordInput, Select, CheckboxInput
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from . import validators, models
logger = logging.getLogger('tasker_account')


class Login(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'username',
                'placeholder': _('username')
            }
        ),
        label=_('username')
    )

    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'current-password',
                'placeholder': _('Password')
            }
        ),
        label=_('Password')
    )

    remember = forms.BooleanField(
        required=False,
        widget=CheckboxInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_CHECK_INPUT_CLASS', 'form-check-input'),
            }
        )

    )

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
        ],
        label=_('Password')
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
        ],
        label=_('Password confirmation')
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
        session.set_expiry(getattr(settings, 'TASKER_ACCOUNT_SESSION_SIGNUP', 60*60*24))

        session['username'] = self.cleaned_data.get('username')
        session['last_name'] = self.cleaned_data.get('last_name')
        session['first_name'] = self.cleaned_data.get('first_name')
        session['email'] = self.cleaned_data.get('email')
        session['password1'] = self.cleaned_data.get('password1')
        session['password2'] = self.cleaned_data.get('password2')
        session['module'] = __name__

        if hasattr(self.request, 'GET'):
            session['next'] = self.request.GET.get('next', '/')
        else:
            session['next'] = '/'

        session.create()

        if hasattr(self.request, 'get_host'):
            host = self.request.get_host()
        else:
            host = 'localhost'

        subject = render_to_string('django_tasker_account/email/signup.subject.txt', {}).strip()

        url = reverse('django_tasker_account:confirm_email', kwargs={'data': session.session_key})

        body = render_to_string('django_tasker_account/email/signup.body.html', {
            'session_key': session.session_key,
            'host': host,
            'url': url,
        })

        name_email = getattr(settings, 'EMAIL_NAME', settings.DEFAULT_FROM_EMAIL)
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=formataddr((name_email, settings.DEFAULT_FROM_EMAIL)),
            to=[self.cleaned_data.get('email')],
            headers={'Message-ID': make_msgid(domain=host)},
        )
        msg.content_subtype = "html"
        msg.send()

        logger.debug("Confirmation code: {session}".format(session=session.session_key))
        return session

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

    def sendmail(self) -> import_module(settings.SESSION_ENGINE).SessionStore:
        session_store = import_module(settings.SESSION_ENGINE).SessionStore

        user = self.user()

        session = session_store()
        session.set_expiry(getattr(settings, 'TASKER_ACCOUNT_SESSION_FORGOTPASSWORD', 60*60*24))
        session['user_id'] = user.id
        session['module'] = __name__

        if hasattr(self.request, 'GET'):
            session['next'] = self.request.GET.get('next', '/')
        else:
            session['next'] = '/'

        session.create()

        if hasattr(self.request, 'get_host'):
            host = self.request.get_host()
        else:
            host = 'localhost'

        subject = render_to_string('django_tasker_account/email/forgot_password.subject.txt', {}).strip()

        url = reverse('django_tasker_account:change_password', kwargs={'data': session.session_key})

        body = render_to_string('django_tasker_account/email/forgot_password.body.html', {
            'session_key': session.session_key,
            'host': host,
            'url': url,
        })

        name_email = getattr(settings, 'EMAIL_NAME', settings.DEFAULT_FROM_EMAIL)
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=formataddr((name_email, settings.DEFAULT_FROM_EMAIL)),
            to=[self.cleaned_data.get('email')],
            headers={'Message-ID': make_msgid(domain=host)},
        )
        msg.content_subtype = "html"
        msg.send()
        return session

    def user(self):
        return get_object_or_404(User, email=self.cleaned_data.get('email'))


class ChangePassword(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'new-password',
                'placeholder': _('Password')
            }
        ),
        label=_('New password')
    )

    new_password2 = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'new-password',
                'placeholder': _('New password confirmation')
            }
        ),
        label=_('New password confirmation')
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def login(self) -> User:
        """
        User authorization
        """
        auth.login(self.request, self.user)
        logger.info("User authentication username:{username}".format(username=self.user.username))
        return self.user


class ProfileChangePassword(PasswordChangeForm):
    new_password1 = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'new-password',
                'placeholder': _('Password')
            }
        ),
        label=_('New password')
    )

    new_password2 = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'new-password',
                'placeholder': _('New password confirmation')
            }
        ),
        label=_('New password confirmation')
    )

    old_password = forms.CharField(
        widget=PasswordInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('Old password')
            }
        ),
        label=_('Old password')
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def login(self) -> User:
        """
        User authorization
        """
        auth.login(self.request, self.user)
        logger.info("User authentication username:{username}".format(username=self.user.username))
        return self.user


class OAuth(forms.Form):
    username = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('username')
            }
        ),
        validators=[
            validators.username,
            validators.username_dublicate,
        ],
        label=_('username')
    )


class Profile(forms.Form):
    GENDER = [
        (1, _('Male')),
        (2, _('Female')),
    ]

    last_name = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('last name')
            },
        ),
        label=_('last name'),
    )

    first_name = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('first name')
            }
        ),
        label=_('first name'),
    )

    gender = forms.ChoiceField(
        choices=GENDER,
        widget=Select(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
            }
        ),
        label=_('gender'),
    )

    birth_date = forms.DateField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'type': 'date',
                'placeholder': _('Birth date')
            }
        ),
        label=_('Birth date'),
    )

    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        widget=Select(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
            }
        ),
        label=_('language'),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def save(self):
        user = get_object_or_404(User, id=self.request.user.id)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()

        profile = get_object_or_404(models.Profile, user=self.request.user)
        profile.language = self.cleaned_data.get('language')
        profile.birth_date = self.cleaned_data.get('birth_date')
        profile.gender = self.cleaned_data.get('gender')
        profile.save()

        logger.info("User profile update id:{id}, first_name:{first_name}, last_name:{last_name}, language:{language}, "
                    "birth_date:{birth_date}, gender:{gender}".format(
            id=self.request.user.id,
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            language=self.cleaned_data.get('language'),
            birth_date=self.cleaned_data.get('birth_date'),
            gender=self.cleaned_data.get('gender'),
        ))


class MyLocation(forms.Form):
    location = forms.CharField(
        widget=TextInput(
            attrs={
                'class': getattr(settings, 'TASKER_HTML_INPUT_CLASS', 'form-control'),
                'autocomplete': 'off',
                'placeholder': _('location')
            }
        ),
        label=_('location')
    )


class Avatar(forms.Form):
    avatar = forms.ImageField()

