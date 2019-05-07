from django.urls import path, register_converter
from . import views, converters

register_converter(converters.ConfirmEmail, 'confirm_email')
register_converter(converters.ChangePassword, 'change_password')
register_converter(converters.OAuth, 'oauth')

urlpatterns = [
    path('login/', views.login),
    path('signup/', views.signup),
    path('forgot_password/', views.forgot_password),
    path('confirm/email/<confirm_email:data>/', views.confirm_email),
    path('change/password/<change_password:data>/', views.change_password),

    path('oauth/yandex/', views.oauth_yandex),
    path('oauth/google/', views.oauth_google),
    path('oauth/vk/', views.oauth_vk),
    path('oauth/facebook/', views.oauth_facebook),
    path('oauth/mailru/', views.oauth_mailru),
    path('oauth/completion/<oauth:data>/', views.oauth_completion, name="oauth_completion"),
]
