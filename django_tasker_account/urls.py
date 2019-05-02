from django.urls import path, register_converter
from . import views, converters

register_converter(converters.ConfirmEmail, 'confirm_email')
register_converter(converters.ChangePassword, 'change_password')

urlpatterns = [
    path('login/', views.login),
    path('signup/', views.signup),
    path('forgot_password/', views.forgot_password),
    path('confirm/email/<confirm_email:data>/', views.confirm_email),
    path('change/password/<change_password:data>/', views.change_password),
]
