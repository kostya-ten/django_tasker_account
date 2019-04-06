from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'gender', 'birth_date', 'phone')


admin.site.register(Profile, ProfileAdmin)
