import json

from django.contrib.sessions.models import Session
from django.contrib import admin
from .models import Profile, Oauth


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'gender', 'birth_date', 'phone', 'geobase')


class OAuthAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'expires_in')
    readonly_fields = ('oauth_id', 'user', 'provider', 'expires_in', 'access_token')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class SessionAdmin(admin.ModelAdmin):
    @staticmethod
    def _session_data(obj):
        json_string = json.dumps(obj.get_decoded())
        return json_string

    _session_data.allow_tags = True
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data']
    exclude = ['session_data']
    date_hierarchy = 'expire_date'


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Oauth, OAuthAdmin)
