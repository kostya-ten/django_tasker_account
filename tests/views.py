import logging

from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render


logger = logging.getLogger('tasker_account')


@login_required
def index(request: WSGIRequest):
    return render(request, 'index.html')
