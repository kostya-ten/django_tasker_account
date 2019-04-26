from django.urls import path, register_converter
from . import views, converters

register_converter(converters.ConfirmEmail, 'confirm_email')

urlpatterns = [
    path('login/', views.login),
    path('signup/', views.signup),
    path('confirm/email/<confirm_email:data>/', views.confirm_email),
]
