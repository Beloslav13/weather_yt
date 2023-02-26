import sys

from django.core.management import BaseCommand, CommandError

from weather.services.base_weather import save_weather
from weather.services.openweather import OpenWeatherAPI, DBOpenWeatherStorage


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--lat', type=str, required=True)
        parser.add_argument('--long', type=str, required=True)
        # parser.add_argument('--method', type=str, required=True)

    def handle(self, *args, **options):
        sys.stdout.write("Run...\n")
        openweather = OpenWeatherAPI(options.get("lat"), options.get("long"))
        result = openweather.get_weather()
        if result is None:
            raise CommandError("Sorry, response is None.")

        storage = DBOpenWeatherStorage(result)
        save_weather(storage)
        sys.stdout.write("Done!\n")
