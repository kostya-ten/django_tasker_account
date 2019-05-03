from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.utils.translation import gettext_lazy as _

from . import forms, geobase, converters


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

