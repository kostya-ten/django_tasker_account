from django.conf import settings
from django.contrib import auth
from django.shortcuts import render, redirect

from . import models, forms


def login(request):
    if request.method == 'GET':
        return render(request, "tasker_account/login.html", {'form': forms.Login()})

    form = forms.Login(data=request.POST, request=request)
    if form.is_valid():
        form.login()
        return redirect(request.GET.get('next', settings.LOGIN_REDIRECT_URL))

    return render(request, 'tasker_account/login.html', {'form': form}, status=400)


def signup(request):
    if request.method == 'GET':
        return render(request, "tasker_account/signup.html", {'form': forms.Signup()})

    form = forms.Signup(data=request.POST, request=request)
    if form.is_valid():
        form.confirmation()

    return render(request, "tasker_account/signup.html", {'form': form})
