import logging
import os
import hashlib
from importlib import import_module

import requests

from pprint import pprint
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from email_validator import validate_email

from . import forms, geobase, converters, views, models

logger = logging.getLogger('tasker_account')


def login(request: WSGIRequest):
    """View for user authentication"""
    if request.method == 'GET':
        return render(request, "django_tasker_account/login.html", {'form': forms.Login()})

    form = forms.Login(data=request.POST, request=request)
    if form.is_valid():
        form.login()
        return redirect(request.GET.get('next', settings.LOGIN_REDIRECT_URL))

    return render(request, 'django_tasker_account/login.html', {'form': form}, status=400)


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
        #user.profile.language = get_supported_language_variant(get_language_from_request(request))
        user.profile.geobase = geobase.detect_ip(query=request)
        user.profile.save()

        messages.success(request, _("Your address has been successfully verified"))
        return redirect(data.next)

    return redirect(settings.LOGIN_URL)


def forgot_password(request: WSGIRequest):
    if request.method == 'GET':
        return render(request, "django_tasker_account/forgot_password.html", {'form': forms.ForgotPassword()})

    form = forms.ForgotPassword(data=request.POST, request=request)
    if form.is_valid():
        form.sendmail()
        messages.success(request, _("You have been sent a link to change your password"))
        return redirect(settings.LOGIN_URL)

    return render(request, "django_tasker_account/forgot_password.html", {'form': form}, status=400)


def change_password(request: WSGIRequest, data: converters.ChangePassword):
    if request.method == 'GET':
        form = forms.ChangePassword(user=data.user_id)
        return render(request, "django_tasker_account/change_password.html", {'form': form})

    form = forms.ChangePassword(data=request.POST, request=request, user=data.user)
    if form.is_valid():
        form.save()
        form.login()
        data.session.delete()
        messages.success(request, _("Password successfully changed"))
        return redirect(data.next)

    return render(request, "django_tasker_account/change_password.html", {'form': form}, status=400)


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

    request.session["oauth"] = {
        'server': 2,
        'access_token': json.get('access_token'),
        'refresh_token': json.get('refresh_token'),
        'token_type': json.get('token_type'),

        'id': json_info.get('id'),
        'birth_date': json_info.get('birthday'),
        'last_name': json_info.get('last_name'),
        'first_name': json_info.get('first_name'),
    }

    if json_info.get('sex') == 'male':
        request.session["oauth"]["gender"] = 1
    elif json_info.get('sex') == 'female':
        request.session["oauth"]["gender"] = 2
    else:
        request.session["oauth"]["gender"] = None

    if not json_info.get('is_avatar_empty'):
        request.session["oauth"]["avatar"] = "https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200".format(
            avatar_id=json_info.get('default_avatar_id')
        )
    else:
        request.session["oauth"]["avatar"] = None

    # Verifying that the user is registered with yandex domains
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

    request.session["oauth"]["email"] = email

    # Check login
    user = str(user).replace(".", "_")
    if not models.User.objects.filter(username=user).exists():
        request.session["oauth"]["username"] = user
    else:
        request.session["oauth"]["username"] = "{user}#yandex".format(user=user)

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))
    request.session["oauth"]["expires_in"] = dt.isoformat()

    return redirect(reverse(views.oauth_completion))


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

    request.session["oauth"] = {
        'server': 1,
        'access_token': json.get('access_token'),
        'refresh_token': None,
        'token_type': json.get('token_type'),

        'id': json_info.get('id'),
        'birth_date': None,
        'avatar': json_info.get('picture'),
        'last_name': json_info.get('family_name'),
        'first_name': json_info.get('given_name'),
    }

    if json_info.get('verified_email'):
        email = json_info.get('email').strip().lower()
        user = email.rsplit('@', 1)[0]

        if validate_email(email).get('domain') != 'gmail.com':
            messages.error(request, _('Allowed to use for authorization domain gmail.com'))
            return redirect(settings.LOGIN_URL)

        request.session["oauth"]["email"] = email

        # Check login
        user = str(user).replace(".", "_")
        if not models.User.objects.filter(username=user).exists():
            request.session["oauth"]["username"] = user
        else:
            request.session["oauth"]["username"] = "{user}#google".format(user=user)

    else:
        request.session["oauth"]["email"] = None
        request.session["oauth"]["username"] = "{username}#google".format(username=json_info.get('id'))

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))
    request.session["oauth"]["expires_in"] = dt.isoformat()

    return redirect(reverse(views.oauth_completion))


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

    request.session["oauth"] = {
        'server': 4,
        'access_token': json.get('access_token'),
        'refresh_token': None,
        'token_type': None,

        'id': json.get('user_id'),
        'birth_date': None,
        'avatar': json_info.get('photo_200'),
        'last_name': json_info.get('last_name'),
        'first_name': json_info.get('first_name'),
        'email': None,

    }

    # Check login
    user = json_info.get('screen_name').replace(".", "_")
    if not models.User.objects.filter(username=user).exists():
        request.session["oauth"]["username"] = user
    else:
        request.session["oauth"]["username"] = "{user}#vk".format(user=user)

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))
    request.session["oauth"]["expires_in"] = dt.isoformat()

    return redirect(reverse(views.oauth_completion))


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

    picture = None
    if json_info.get('picture') and json_info.get('picture').get('data'):
        picture = json_info.get('picture').get('data').get('url')

    dt = datetime.now(timezone.utc) + timedelta(seconds=json.get('expires_in'))

    session_store = import_module(settings.SESSION_ENGINE).SessionStore
    session = session_store()

    session['server'] = 5,
    session['access_token'] = json.get('access_token'),
    session['id'] = json_info.get('id'),
    session['birth_date'] = None,
    session['avatar'] = picture,
    session['last_name'] = json_info.get('last_name'),
    session['first_name'] = json_info.get('first_name'),
    session['email'] = None,
    session['username'] = None,
    session['expires_in'] = dt.isoformat(),
    session['module'] = __name__,
    session.create()

    return redirect("{url}{session_key}/".format(url=reverse(views.oauth_completion), session_key=session.session_key))


def oauth_completion(request: WSGIRequest, data: converters.OAuth):
    oauth = request.session.get('oauth')
    del request.session['oauth']
    pprint(oauth)

    if not oauth:
        messages.error(request, _('Maybe your account has already been activated'))
        return redirect(settings.LOGIN_URL)

    return render(request, 'django_tasker_account/oauth_completion.html', {'form': forms.OAuth()})

    # m = hashlib.sha512()
    # m.update(oauth.get('id').encode("utf-8"))
    #
    # # If the user is already registered through OAuth
    # result = models.Oauth.objects.filter(oauth_id=m.hexdigest(), server=oauth.get('server'))
    # if result.exists():
    #     user = result.get(oauth_id=m.hexdigest(), server=oauth.get('server')).user
    #     auth.login(request, user)
    #
    #     if oauth.get('gender') and not user.profile.gender:
    #         user.profile.gender = oauth.get('gender')
    #         user.profile.save()
    #
    #     if oauth.get('birth_date') and not user.profile.birth_date:
    #         user.profile.birth_date = oauth.get('birth_date')
    #         user.profile.save()
    #
    #     if oauth.get('avatar') and not user.profile.avatar:
    #         response = requests.get(oauth.get('avatar'))
    #         if response.status_code == 200:
    #             user.profile.avatar.save('avatar.png', ContentFile(response.content))
    #
    #     if not user.profile.geobase:
    #         user.profile.geobase = geobase.detect_ip(query=request)
    #         user.profile.save()
    #
    #     return redirect(oauth.get('next', '/'))
    #
    # # If the email user is the same as the account already registered
    # user = None
    # if oauth.get('email'):
    #     user = models.User.objects.filter(email=oauth.get('email'))
    #     if user.exists():
    #         user = user.last()
    #
    # if not user:
    #     # Registration user
    #
    #     if not models.User.objects.filter(username=oauth.get('username')).exists():
    #         raise Exception("Username is exists")
    #
    #     user = User.objects.create_user(
    #         username=oauth.get('username'),
    #         email=oauth.get('email'),
    #         first_name=oauth.get('first_name'),
    #         last_name=oauth.get('last_name')
    #     )
    #     user.save()
    #
    # # Link with the model Oauth
    # models.Oauth.objects.create(
    #     oauth_id=m.hexdigest(),
    #     server=oauth.get('server'),
    #     access_token=oauth.get('access_token'),
    #     refresh_token=oauth.get('refresh_token'),
    #     expires_in=oauth.get('expires_in'),
    #     user=user,
    # )
    #
    # # Authentication
    # auth.login(request, user)
    #
    # if oauth.get('gender') and not user.profile.gender:
    #     user.profile.gender = oauth.get('gender')
    #     user.profile.save()
    #
    # if oauth.get('birth_date') and not user.profile.birth_date:
    #     user.profile.birth_date = oauth.get('birth_date')
    #     user.profile.save()
    #
    # if oauth.get('avatar') and not user.profile.avatar:
    #     response = requests.get(oauth.get('avatar'))
    #     if response.status_code == 200:
    #         user.profile.avatar.save('avatar.png', ContentFile(response.content))
    #
    # if oauth.get('last_name') and not user.last_name:
    #     user.last_name = oauth.get('last_name')
    #     user.save()
    #
    # if oauth.get('first_name') and not user.first_name:
    #     user.last_name = oauth.get('first_name')
    #     user.save()
    #
    # user.profile.geobase = geobase.detect_ip(query=request)
    # user.profile.save()
    #
    # return redirect(oauth.get('next', '/'))
