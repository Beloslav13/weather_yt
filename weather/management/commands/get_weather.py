from django.core.management import BaseCommand

from weather.services.base_weather import save_weather
from weather.services.openweather import OpenWeatherAPI, DBOpenWeatherStorage


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--lat', type=str, required=True)
        parser.add_argument('--long', type=str, required=True)
        # parser.add_argument('--method', type=str, required=True)

    def handle(self, *args, **options):
        openweather = OpenWeatherAPI(options.get("lat"), options.get("long"))
        result = openweather.get_weather()
        storage = DBOpenWeatherStorage(result)
        save_weather(storage)
