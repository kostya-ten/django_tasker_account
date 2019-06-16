from django.urls import path, register_converter
from . import views, converters

register_converter(converters.ConfirmEmail, 'confirm_email')
register_converter(converters.ChangePassword, 'change_password')
register_converter(converters.OAuth, 'oauth')

app_name = 'django_tasker_account'

urlpatterns = [
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('signup/', views.signup, name="signup"),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('confirm/email/<confirm_email:data>/', views.confirm_email, name="confirm_email"),
    path('change/password/<change_password:data>/', views.change_password, name="change_password"),

    path('oauth/yandex/', views.oauth_yandex, name="oauth_yandex"),
    path('oauth/google/', views.oauth_google, name="oauth_google"),
    path('oauth/vk/', views.oauth_vk, name="oauth_vk"),
    path('oauth/facebook/', views.oauth_facebook, name="oauth_facebook"),
    path('oauth/mailru/', views.oauth_mailru, name="oauth_mailru"),
    path('oauth/completion/<oauth:data>/', views.oauth_completion, name="oauth_completion"),

    path('profile/', views.profile, name="profile"),
    path('profile/change/password/', views.profile_change_password, name="profile_change_password"),
    path('profile/mylocation/', views.profile_mylocation, name="profile_mylocation"),
    path('profile/avatar/', views.profile_avatar, name="profile_avatar"),
]
