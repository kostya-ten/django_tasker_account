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
        return redirect(request.POST.get('next', '/'))

    return render(request, 'tasker_account/login.html', {'form': form}, status=400)
