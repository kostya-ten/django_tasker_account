from django.conf import settings
from django.contrib import auth
from django.shortcuts import render, redirect

from . import models, forms

"""
views.py
====================================
The core module of my example project
"""


def login(request):
    """
    Return the most important thing about a person.
    Parameters
    ----------
    your_name
        A string indicating the name of the person.
    """
    if request.method == 'GET':
        return render(request, "django_tasker_account/login.html", {'form': forms.Login()})

    form = forms.Login(data=request.POST, request=request)
    if form.is_valid():
        form.login()
        return redirect(request.GET.get('next', settings.LOGIN_REDIRECT_URL))

    return render(request, 'django_tasker_account/login.html', {'form': form}, status=400)


def signup(request):
    if request.method == 'GET':
        return render(request, "django_tasker_account/signup.html", {'form': forms.Signup()})

    form = forms.Signup(data=request.POST, request=request)
    if form.is_valid():
        form.confirmation()

    return render(request, "django_tasker_account/signup.html", {'form': form})
