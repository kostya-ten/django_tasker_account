import logging
import os
import hashlib
import re
import requests

from importlib import import_module

from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.core.files.storage import default_storage
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from email_validator import validate_email

from . import forms, geobase, converters, models

logger = logging.getLogger('tasker_account')


def login(request: WSGIRequest):
    """View for user authentication"""
    if request.method == 'GET':
        return render(request, "django_tasker_account/login.html", {'form': forms.Login()})

    form = forms.Login(data=request.POST, request=request)
    if form.is_valid():
        user = form.login()
        logger.info("Login user username:{username}".format(username=user.username))
        return redirect(request.GET.get('next', settings.LOGIN_REDIRECT_URL))

    return render(request, 'django_tasker_account/login.html', {'form': form}, status=400)


def logout(request: WSGIRequest):
    if request.user.is_authenticated:
        logger.info("Logout user username:{username}".format(username=request.user.username))
        auth.logout(request)

    return redirect('/')
    # return redirect(settings.LOGOUT_REDIRECT_URL)


def signup(request: WSGIRequest):
    """View for user registration"""
    if request.method == 'GET':
        return render(request, "django_tasker_account/signup.html", {'form': forms.Signup()})

    form = forms.Signup(data=request.POST, request=request)
    if form.is_valid():
        form.confirmation()
        messages.success(request, _("A confirmation email has been sent to your email address"))
        return redirect(settings.LOGIN_URL)

    return render(request, "django_tasker_account/signup.html", {'form': form}, status=400)


def confirm_email(request: WSGIRequest, data: converters.ConfirmEmail):
    """View for confirmation email address"""
    form = forms.Signup(data={
        'username': data.username,
        'last_name': data.last_name,
        'first_name': data.first_name,
        'email': data.email,
        'password1': data.password1,
        'password2': data.password2,
    })

    if form.is_valid():
        user = form.save()
        data.session.delete()
        auth.login(request, user)

        # Set language profile
        # user.profile.language = get_supported_language_variant(get_language_from_request(request))
        user.profile.geobase = geobase.detect_ip(query=request)
        user.profile.save()

        messages.success(request, _("Your address has been successfully verified"))
        return redirect(data.next)

    return redirect(settings.LOGIN_URL)


def forgot_password(request: WSGIRequest):
    """View forgot password"""
    if request.method == 'GET':
        return render(request, "django_tasker_account/forgot_password.html", {'form': forms.ForgotPassword()})

    form = forms.ForgotPassword(data=request.POST, request=request)
    if form.is_valid():
        form.sendmail()
        messages.success(request, _("Password reset sent"))
        return redirect(settings.LOGIN_URL)

    return render(request, "django_tasker_account/forgot_password.html", {'form': form}, status=400)


def change_password(request: WSGIRequest, data: converters.ChangePassword):
    """Password change view"""
    if request.method == 'GET':
        form = forms.ChangePassword(user=data.user_id)
        return render(request, "django_tasker_account/change_password.html", {'form': form})

    form = forms.ChangePassword(data=request.POST, request=request, user=data.user)
    if form.is_valid():
        form.save()
        form.login()
        data.session.delete()
        messages.success(request, _("Password reset complete"))
        return redirect(data.next)

    return render(request, "django_tasker_account/change_password.html", {'form': form}, status=400)


def oauth_google(request: WSGIRequest):
    client_id = getattr(settings, 'OAUTH_GOOGLE_CLIENT_ID', os.environ.get('OAUTH_GOOGLE_CLIENT_ID'))
    client_secret = getattr(settings, 'OAUTH_GOOGLE_SECRET_KEY', os.environ.get('OAUTH_GOOGLE_SECRET_KEY'))

    if not client_id:
        logger.error(_("Application OAuth Google is disabled"))
        messages.error(request, _("Application OAuth Google is disabled"))
        return redirect('/')

    redirect_uri = "{shema}://{host}{path}".format(
        shema=request.META.get('HTTP_X_FORWARDED_PROTO', request.scheme),
        host=request.get_host(),
        path=request.path,
    )

    if not request.GET.get('code'):
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': request.GET.get('next', '/'),
            'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
        }

        redirect_url = "https://accounts.google.com/o/oauth2/v2/auth?{param}".format(param=urlencode(params))
        return redirect(redirect_url)

    data = {
        'grant_type': 'authorization_code',
        'code': request.GET.get('code'),
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
    }

    response = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
    json = response.json()

    response_info = requests.get(
        url='https://www.googleapis.com/oauth2/v1/userinfo',
        params={'format': 'json'},
        headers={'Authorization': 'OAuth ' + json.get('access_token')})

    json_info = response_info.json()

    session_store = import_module(settings.SESSION_ENGINE).SessionStore
    session = session_store()

    m = hashlib.sha256()
    m.update(str(json_info.get('id')).encode("utf-8"))

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))

    session["oauth"] = {
        'provider': 1,
        'id': m.hexdigest(),
        'access_token': json.get('access_token'),
        'birth_date': None,
        'gender': None,
        'avatar': json_info.get('picture'),
        'last_name': json_info.get('family_name'),
        'first_name': json_info.get('given_name'),
        'username': None,
        'module': __name__,
        'expires_in': dt.isoformat(),
        'next': request.GET.get('state')
    }

    if json_info.get('verified_email'):
        email = json_info.get('email').strip().lower()
        user = email.rsplit('@', 1)[0]

        if validate_email(email).get('domain') != 'gmail.com':
            messages.error(request, _('Allowed to use for authorization domain gmail.com'))
            return redirect(settings.LOGIN_URL)

        user = str(user).replace(".", "_")
        if not models.User.objects.filter(username=user).exists():
            session["oauth"]["username"] = user

        session["oauth"]["email"] = email

    session.create()
    return redirect(reverse('django_tasker_account:oauth_completion', kwargs={'data': session.session_key}))


def oauth_yandex(request: WSGIRequest):
    client_id = getattr(settings, 'OAUTH_YANDEX_CLIENT_ID', os.environ.get('OAUTH_YANDEX_CLIENT_ID'))
    client_secret = getattr(settings, 'OAUTH_YANDEX_SECRET_KEY', os.environ.get('OAUTH_YANDEX_SECRET_KEY'))

    if not client_id:
        logger.error(_("Application OAuth Yandex is disabled"))
        messages.error(request, _("Application OAuth Yandex is disabled"))
        return redirect('/')

    redirect_uri = "{shema}://{host}{path}".format(
        shema=request.META.get('HTTP_X_FORWARDED_PROTO', request.scheme),
        host=request.get_host(),
        path=request.path,
    )

    if request.GET.get('error'):
        logger.error(_("User denied access to data"))
        messages.error(request, _("User denied access to data"))
        return redirect(settings.LOGIN_URL)

    if not request.GET.get('code'):
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': request.GET.get('next', '/'),
        }

        if settings.DEBUG:
            params['force_confirm'] = 'yes'

        return redirect('https://oauth.yandex.ru/authorize?' + urlencode(params))

    data = {
        'grant_type': 'authorization_code',
        'code': request.GET.get('code'),
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
    }

    response = requests.post('https://oauth.yandex.ru/token', data=data)
    json = response.json()

    response_info = requests.get(
        url='https://login.yandex.ru/info',
        params={'format': 'json'},
        headers={'Authorization': 'OAuth ' + json.get('access_token')},
    )

    json_info = response_info.json()

    session_store = import_module(settings.SESSION_ENGINE).SessionStore
    session = session_store()

    m = hashlib.sha256()
    m.update(str(json_info.get('id')).encode("utf-8"))

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))

    session["oauth"] = {
        'provider': 2,
        'id': m.hexdigest(),
        'access_token': json.get('access_token'),
        'birth_date': json_info.get('birthday'),
        'last_name': json_info.get('last_name'),
        'first_name': json_info.get('first_name'),
        'expires_in': dt.isoformat(),
        'module': __name__,
        'next': request.GET.get('state')
    }

    if not json_info.get('is_avatar_empty'):
        session["oauth"]["avatar"] = "https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200".format(
            avatar_id=json_info.get('default_avatar_id')
        )
    else:
        session["oauth"]["avatar"] = None

    if json_info.get('sex') == 'male':
        session["oauth"]["gender"] = 1
    elif json_info.get('sex') == 'female':
        session["oauth"]["gender"] = 2
    else:
        session["oauth"]["gender"] = None

    email = json_info.get('default_email').strip().lower()
    user = email.rsplit('@', 1)[0]
    domain = email.rsplit('@', 1)[-1]

    if domain == 'ya.ru' or \
            domain == 'yandex.by' or \
            domain == 'yandex.com' or \
            domain == 'yandex.kz' or \
            domain == 'yandex.ua':
        email = '{user}@yandex.ru'.format(user=user)

    if validate_email(email).get('domain') != 'yandex.ru':
        messages.error(request, _('Allowed to use for authorization domain yandex.ru'))
        return redirect(settings.LOGIN_URL)

    # Check login
    user = str(user).replace(".", "_")
    if not models.User.objects.filter(username=user).exists():
        session["oauth"]["username"] = user
    else:
        session["oauth"]["username"] = None

    session["oauth"]["email"] = email
    session.create()

    return redirect(reverse('django_tasker_account:oauth_completion', kwargs={'data': session.session_key}))


def oauth_mailru(request: WSGIRequest):
    client_id = getattr(settings, 'OAUTH_MAILRU_CLIENT_ID', os.environ.get('OAUTH_MAILRU_CLIENT_ID'))
    client_secret = getattr(settings, 'OAUTH_MAILRU_SECRET_KEY', os.environ.get('OAUTH_MAILRU_SECRET_KEY'))

    if not client_id:
        logger.error(_("Application OAuth Mail.ru is disabled"))
        messages.error(request, _("Application OAuth Mail.ru is disabled"))
        return redirect('/')

    redirect_uri = "{shema}://{host}{path}".format(
        shema=request.META.get('HTTP_X_FORWARDED_PROTO', request.scheme),
        host=request.get_host(),
        path=request.path,
    )

    if request.GET.get('error'):
        logger.error(_("User denied access to data"))
        messages.error(request, _("User denied access to data"))
        return redirect(settings.LOGIN_URL)

    if not request.GET.get('code'):
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'userinfo',
            'state': request.GET.get('next', '/'),
        }

        return redirect('https://oauth.mail.ru/login?' + urlencode(params))

    data = {
        'grant_type': 'authorization_code',
        'code': request.GET.get('code'),
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
    }
    response = requests.post('https://oauth.mail.ru/token', data=data)
    json = response.json()

    response_info = requests.get('https://oauth.mail.ru/userinfo', params={'access_token': json.get('access_token')})
    json_info = response_info.json()

    session_store = import_module(settings.SESSION_ENGINE).SessionStore
    session = session_store()

    m = hashlib.sha256()
    m.update(str(json_info.get('email')).encode("utf-8"))

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))

    session["oauth"] = {
        'provider': 3,
        'id': m.hexdigest(),
        'access_token': json.get('access_token'),
        'birth_date': None,
        'last_name': json_info.get('last_name'),
        'first_name': json_info.get('first_name'),
        'email': json_info.get('email'),
        'username': None,
        'avatar': json_info.get('image'),
        'expires_in': dt.isoformat(),
        'module': __name__,
        'next': request.GET.get('state')
    }

    if json_info.get('gender') == 'm':
        session["oauth"]["gender"] = 1
    elif json_info.get('gender') == 'f':
        session["oauth"]["gender"] = 2
    else:
        session["oauth"]["gender"] = None

    email = json_info.get('email').strip().lower()
    user = email.rsplit('@', 1)[0]
    domain = email.rsplit('@', 1)[-1]

    if domain != 'mail.ru' and domain != 'bk.ru' and domain != 'list.ru' and domain != 'inbox.ru':
        messages.error(request, _('Allowed to use for authorization domain mail.ru, bk.ru, list.ru, inbox.ru'))
        return redirect(settings.LOGIN_URL)

    # Check login
    user = str(user).replace(".", "_")
    if not models.User.objects.filter(username=user).exists():
        session["oauth"]["username"] = user
    else:
        session["oauth"]["username"] = None

    session["oauth"]["email"] = email
    session["oauth"]["birth_date"] = datetime.strptime(json_info.get('birthday'), "%d.%m.%Y").strftime("%Y-%m-%d")

    session.create()

    return redirect(reverse('django_tasker_account:oauth_completion', kwargs={'data': session.session_key}))


def oauth_vk(request: WSGIRequest):
    client_id = getattr(settings, 'OAUTH_VK_CLIENT_ID', os.environ.get('OAUTH_VK_CLIENT_ID'))
    client_secret = getattr(settings, 'OAUTH_VK_SECRET_KEY', os.environ.get('OAUTH_VK_SECRET_KEY'))

    if not client_id:
        logger.error(_("Application OAuth Vk.com is disabled"))
        messages.error(request, _("Application OAuth Vk.com is disabled"))
        return redirect('/')

    redirect_uri = "{shema}://{host}{path}".format(
        shema=request.META.get('HTTP_X_FORWARDED_PROTO', request.scheme),
        host=request.get_host(),
        path=request.path,
    )

    if not request.GET.get('code'):
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': request.GET.get('next', '/'),
        }

        redirect_url = "https:///oauth.vk.com/authorize?{param}".format(param=urlencode(params))
        return redirect(redirect_url)

    data = {
        'grant_type': 'authorization_code',
        'code': request.GET.get('code'),
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
    }

    response = requests.post('https://oauth.vk.com/access_token', data=data)
    json = response.json()

    response_info = requests.post('https://api.vk.com/method/users.get', data={
        'user_ids': json.get('user_id'),
        'fields': 'first_name,last_name,bdate,photo_200,screen_name',
        'access_token': json.get('access_token'),
        'v': '5.95',
    })
    json_info = response_info.json()
    json_info = json_info.get('response').pop()

    session_store = import_module(settings.SESSION_ENGINE).SessionStore
    session = session_store()

    m = hashlib.sha256()
    m.update(str(json.get('user_id')).encode("utf-8"))

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))

    session["oauth"] = {
        'provider': 4,
        'id': m.hexdigest(),
        'access_token': json.get('access_token'),
        'birth_date': json_info.get('birthday'),
        'last_name': json_info.get('last_name'),
        'first_name': json_info.get('first_name'),
        'email': None,
        'gender': None,
        'avatar': json_info.get('photo_200'),
        'username': None,
        'expires_in': dt.isoformat(),
        'module': __name__,
        'next': request.GET.get('state')
    }

    if not re.match(r'^id[0-9]+', json_info.get('screen_name')):
        user = json_info.get('screen_name').replace(".", "_")
        if not models.User.objects.filter(username=user).exists():
            session["oauth"]["username"] = user

    session.create()
    return redirect(reverse('django_tasker_account:oauth_completion', kwargs={'data': session.session_key}))


def oauth_facebook(request: WSGIRequest):
    client_id = getattr(settings, 'OAUTH_FACEBOOK_CLIENT_ID', os.environ.get('OAUTH_FACEBOOK_CLIENT_ID'))
    client_secret = getattr(settings, 'OAUTH_FACEBOOK_SECRET_KEY', os.environ.get('OAUTH_FACEBOOK_SECRET_KEY'))

    if not client_id:
        logger.error(_("Application OAuth Facebook is disabled"))
        messages.error(request, _("Application OAuth Facebook is disabled"))
        return redirect('/')

    redirect_uri = "{shema}://{host}{path}".format(
        shema=request.META.get('HTTP_X_FORWARDED_PROTO', request.scheme),
        host=request.get_host(),
        path=request.path,
    )

    if not request.GET.get('code'):
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': request.GET.get('next', '/'),
        }

        return redirect('https://www.facebook.com/v3.2/dialog/oauth?' + urlencode(params))

    data = {
        'grant_type': 'authorization_code',
        'code': request.GET.get('code'),
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
    }

    response = requests.post('https://graph.facebook.com/v3.3/oauth/access_token', data=data)
    json = response.json()

    params = {'fields': 'id,first_name,last_name,picture.height(200)'}
    headers = {'Authorization': 'OAuth ' + json.get('access_token')}
    response_info = requests.get('https://graph.facebook.com/v3.2/me', params=params, headers=headers)
    json_info = response_info.json()

    session_store = import_module(settings.SESSION_ENGINE).SessionStore
    session = session_store()

    m = hashlib.sha256()
    m.update(str(json_info.get('id')).encode("utf-8"))

    picture = None
    if json_info.get('picture') and json_info.get('picture').get('data'):
        picture = json_info.get('picture').get('data').get('url')

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))

    session["oauth"] = {
        'provider': 5,
        'id': m.hexdigest(),
        'access_token': json.get('access_token'),
        'birth_date': None,
        'last_name': json_info.get('last_name'),
        'first_name': json_info.get('first_name'),
        'email': None,
        'username': None,
        'avatar': picture,
        'expires_in': dt.isoformat(),
        'module': __name__,
        'next': request.GET.get('state')
    }
    session.create()
    return redirect(reverse('django_tasker_account:oauth_completion', kwargs={'data': session.session_key}))


def oauth_completion(request: WSGIRequest, data: converters.OAuth):
    if request.method == 'POST':
        form = forms.OAuth(data=request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data.get('username'),
                email=data.email,
            )
            _oauth_update_user(user=user, data=data)
            _link_oauth(user=user, data=data)
            data.session.delete()

            # save geobase
            user.profile.geobase = geobase.detect_ip(query=request)
            user.profile.save()

            auth.login(request, user)
            return redirect(data.next)

        return render(request, 'django_tasker_account/oauth_completion.html', {'form': form}, status=400)

    # If the user is already registered through OAuth
    result = models.Oauth.objects.filter(oauth_id=data.id, provider=data.provider)
    if result.exists():
        user = result.get(oauth_id=data.id, provider=data.provider).user
        _oauth_update_user(user=user, data=data)
        auth.login(request, user)
        return redirect(data.next)

    # If the email user is the same as the account already registered
    if data.email:
        user = models.User.objects.filter(email=data.email)
        if user.exists():
            user = user.last()
            _oauth_update_user(user=user, data=data)
            _link_oauth(user=user, data=data)
            data.session.delete()

            # save geobase
            user.profile.geobase = geobase.detect_ip(query=request)
            user.profile.save()

            # Authentication
            auth.login(request, user)
            return redirect(data.next)

    if data.username:
        user = models.User.objects.filter(username=data.username)
        if not user.exists():
            user = User.objects.create_user(
                username=data.username,
                email=data.email,
                last_name=data.last_name,
                first_name=data.first_name,
            )
            _oauth_update_user(user=user, data=data)
            _link_oauth(user=user, data=data)
            data.session.delete()

            # save geobase
            user.profile.geobase = geobase.detect_ip(query=request)
            user.profile.save()

            # Authentication
            auth.login(request, user)
            return redirect(data.next)

    form = forms.OAuth(initial={'username': data.username})
    return render(request, 'django_tasker_account/oauth_completion.html', {'form': form})


@login_required()
def profile(request: WSGIRequest):
    if request.method == 'POST':
        form = forms.Profile(data=request.POST, request=request)
        if form.is_valid():
            form.save()
            return render(request, "django_tasker_account/profile.html", {'form': form})
        else:
            return render(request, "django_tasker_account/profile.html", {'form': form}, status=400)

    user = request.user
    form = forms.Profile(
        initial={
            'last_name': user.last_name,
            'first_name': user.first_name,
            'gender': user.profile.gender,
            'birth_date': user.profile.birth_date,
            'language': user.profile.language,
        }
    )
    return render(request, "django_tasker_account/profile.html", {'form': form})


@login_required()
def profile_change_password(request: WSGIRequest) -> None:
    if request.method == 'POST':
        form = forms.ProfileChangePassword(data=request.POST, request=request, user=request.user)
        if form.is_valid():
            form.save()
            form.login()
            messages.success(request, _("Your password was changed."))
            return redirect(reverse('django_tasker_account:profile'))
        else:
            return render(request, 'django_tasker_account/profile_change_password.html', {'form': form}, status=400)

    form = forms.ProfileChangePassword(user=request.user)
    return render(request, 'django_tasker_account/profile_change_password.html', {'form': form})


@login_required()
def profile_mylocation(request: WSGIRequest) -> None:

    if request.user.profile.language == 'ru':
        initial_data = "{country}, {locality}".format(
            country=request.user.profile.geobase.country.ru,
            locality=request.user.profile.geobase.locality.ru,
        )
    else:
        initial_data = "{country}, {locality}".format(
            country=request.user.profile.geobase.country.en,
            locality=request.user.profile.geobase.locality.en,
        )

    if request.method == 'POST':
        form = forms.MyLocation(data=request.POST)
        if form.is_valid():
            obj = geobase.detect_geo(query=form.cleaned_data.get('location'))
            request.user.profile.geobase = obj
            request.user.profile.save()
            return render(request, 'django_tasker_account/profile_mylocation.html', {'form': form})

        return render(request, 'django_tasker_account/profile_mylocation.html', {'form': form}, status=400)

    form = forms.MyLocation(initial={'location': initial_data})
    return render(request, 'django_tasker_account/profile_mylocation.html', {'form': form})


@login_required()
def profile_avatar(request: WSGIRequest) -> None:
    if request.method == 'POST':
        form = forms.Avatar(data=request.POST, files=request.FILES)
        if form.is_valid():
            if request.user.profile.avatar:
                default_storage.delete(request.user.profile.avatar.path)

            request.user.profile.avatar.save(
               request.FILES.get('avatar').name,
               ContentFile(request.FILES.get('avatar').read())
            )
            messages.success(request, _("Avatar successfully uploaded."))
            return render(request, 'django_tasker_account/profile_avatar.html', {'form': form})

    form = forms.Avatar()
    return render(request, 'django_tasker_account/profile_avatar.html', {'form': form})


# Update user and profile
def _oauth_update_user(user: User, data: converters.OAuth) -> None:
    flag_save_profile = False
    flag_save_user = False

    if data.gender and not user.profile.gender:
        user.profile.gender = data.gender
        flag_save_profile = True

    if data.birth_date and not user.profile.birth_date:
        user.profile.birth_date = data.birth_date
        flag_save_profile = True

    if data.last_name and not user.last_name:
        user.last_name = data.last_name
        flag_save_user = True

    if data.first_name and not user.first_name:
        user.first_name = data.first_name
        flag_save_user = True

    if data.avatar and not user.profile.avatar:
        response = requests.get(data.avatar)
        if response.status_code == 200:
            user.profile.avatar.save('avatar.png', ContentFile(response.content))
            flag_save_profile = True

    if flag_save_profile:
        user.profile.save()

    if flag_save_user:
        user.save()


# Link with the model Oauth
def _link_oauth(user: User, data: converters.OAuth) -> None:
    models.Oauth.objects.create(
        oauth_id=data.id,
        provider=data.provider,
        access_token=data.access_token,
        expires_in=data.expires_in,
        user=user,
    )
