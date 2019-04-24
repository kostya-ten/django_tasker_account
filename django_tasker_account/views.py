from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect

from . import forms


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

    return render(request, "django_tasker_account/signup.html", {'form': form})
