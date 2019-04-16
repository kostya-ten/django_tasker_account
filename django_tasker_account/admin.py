from django.contrib import admin
from .models import Profile, Geobase, GeobaseCountry, GeobaseProvince, GeobaseLocality, GeobaseTimezone


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'gender', 'birth_date', 'phone', 'geobase')


class GeobaseCountryAdmin(admin.ModelAdmin):
    list_display = ('ru', 'en')


class GeobaseProvinceAdmin(admin.ModelAdmin):
    list_display = ('ru', 'en')


class GeobaseLocalityAdmin(admin.ModelAdmin):
    list_display = ('ru', 'en')


class GeobaseTimezoneAdmin(admin.ModelAdmin):
    list_display = ('name',)


class GeobaseAdmin(admin.ModelAdmin):
    list_display = ('country', 'province', 'locality', 'timezone', 'latitude', 'longitude')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(GeobaseCountry, GeobaseCountryAdmin)
admin.site.register(GeobaseProvince, GeobaseProvinceAdmin)
admin.site.register(GeobaseLocality, GeobaseLocalityAdmin)
admin.site.register(GeobaseTimezone, GeobaseTimezoneAdmin)
admin.site.register(Geobase, GeobaseAdmin)
