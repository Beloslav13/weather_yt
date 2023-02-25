from django.contrib import admin

from .models import OpenWeather, OpenWeatherLog


class OpenWeatherAdmin(admin.ModelAdmin):
    list_display = ("id", "open_error", "latitude", "longitude", "sunrise", "sunset")
    list_display_links = ("id", "open_error", "latitude", "longitude", "sunrise", "sunset")
    list_filter = ("id", "open_error__date", "open_error__result")


class OpenWeatherLogAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "result")
    list_display_links = ("id", "date", "result")


admin.site.register(OpenWeather, OpenWeatherAdmin)
admin.site.register(OpenWeatherLog, OpenWeatherLogAdmin)
