import os
from datetime import datetime
from typing import NamedTuple

import requests
from django.utils import timezone
from json import JSONDecodeError

from weather.services.base_weather import Celsius, Coordinate

from weather.models import OpenWeatherLog, OpenWeather

# test data
# data = {'coord': {'lon': 36.56731, 'lat': 50.556},
#         'weather': [{'id': 800, 'main': 'Clear', 'description': 'ясно', 'icon': '01d'}], 'base': 'stations',
#         'main': {'temp': -7.88, 'feels_like': -14.77, 'temp_min': -8.28, 'temp_max': -7.88, 'pressure': 1022,
#                  'humidity': 62}, 'visibility': 10000, 'wind': {'speed': 5, 'deg': 320}, 'clouds': {'all': 0},
#         'dt': 1677153668, 'sys': {'type': 1, 'id': 9030, 'country': 'RU', 'sunrise': 1677126678, 'sunset': 1677164602},
#         'timezone': 10800, 'id': 824987, 'name': 'Gorod Belgorod', 'cod': 200}

API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&lang=ru&units=metric"


class LogOpenWeatherData(NamedTuple):
    date: datetime
    result: bool
    error: dict


class OpenWeatherData(NamedTuple):
    log: LogOpenWeatherData
    city: str
    temp: Celsius
    latitude: Coordinate
    longitude: Coordinate
    sunrise: datetime
    sunset: datetime


class DBOpenWeatherStorage:

    def __init__(self, weather: OpenWeatherData):
        self.weather = weather

    def save(self) -> None:
        try:
            log_instance = OpenWeatherLog.objects.create(
                date=self.weather.log.date,
                result=self.weather.log.result,
                error=self.weather.log.error
            )
            log_instance.save()

            w_instance = OpenWeather.objects.create(
                open_error=log_instance,
                city=self.weather.city,
                temperature=self.weather.temp,
                latitude=self.weather.latitude,
                longitude=self.weather.longitude,
                sunrise=self.weather.sunrise,
                sunset=self.weather.sunset
            )
            w_instance.save()
        except Exception as e:
            print("-----------")
            print(e)
            print("-----------")
        else:
            print(log_instance)
            print(w_instance)


class OpenWeatherAPI:

    def __init__(self, latitude: Coordinate, longitude: Coordinate):
        self.latitude = latitude
        self.longitude = longitude
        self.url = API_URL.format(self.latitude, self.longitude, os.environ.get("API_KEY"))

    def request(self) -> dict:
        error_data = {}
        try:
            data = requests.get(url=self.url).json()
            # raise JSONDecodeError("mother fucker", "error doc", 10)
        except JSONDecodeError as e:
            error_data.update({"error": {"msg": e.msg, "doc": e.doc, "pos": e.pos}})
        except ConnectionError as e:
            error_data.update({"error": {"msg": e}})
        except Exception as e:
            error_data.update({"error": {"msg": e}})
        else:
            return data
        return error_data

    def parse_weather(self, response: dict) -> OpenWeatherData | None:
        if not response:
            return None

        if response.get("error"):
            return self._create_weather_data(error=True, error_data=response["error"])

        weather_data_fields = {}
        self._prepare_weather_fields(response, weather_data_fields)
        return self._create_weather_data(weather_data_fields)

    def _prepare_weather_fields(self, response: dict, weather_data_fields: dict) -> None:
        self.get_city(response, weather_data_fields)
        self.get_coordinate(response['coord'], weather_data_fields)
        self.get_temperature(response, weather_data_fields)
        self.get_sunrise(response, weather_data_fields)
        self.get_sunset(response, weather_data_fields)

    @staticmethod
    def _create_weather_data(weather_data_fields: dict = None, error: bool = False, error_data: dict = None) -> OpenWeatherData:
        if not error:
            result = OpenWeatherData(
                log=LogOpenWeatherData(date=timezone.now(), result=True, error={}),
                city=weather_data_fields["city"],
                temp=weather_data_fields["temp"],
                latitude=weather_data_fields["lat"],
                longitude=weather_data_fields["long"],
                sunrise=weather_data_fields["sunrise"],
                sunset=weather_data_fields["sunset"],
            )
        else:
            result = OpenWeatherData(
                log=LogOpenWeatherData(date=timezone.now(), result=False, error=error_data),
                city="0",
                temp=0,
                latitude=0,
                longitude=0,
                sunrise=timezone.now(),
                sunset=timezone.now(),
            )
        return result

    @staticmethod
    def get_city(data: dict, weather_data: dict) -> None:
        weather_data.update({"city": data["name"]})

    @staticmethod
    def get_coordinate(data: dict, weather_data: dict) -> None:
        coordinate = Coordinate(data['lat'], data['lon'])
        weather_data.update({"lat": coordinate.latitude, "long": coordinate.longitude})

    @staticmethod
    def get_temperature(data: dict, weather_data: dict) -> None:
        temp = data['main']['temp']
        weather_data.update({"temp": Celsius(temp)})

    @staticmethod
    def get_sunrise(data: dict, weather_data: dict) -> None:
        weather_data.update({"sunrise": datetime.fromtimestamp(data['sys']['sunrise'])})

    @staticmethod
    def get_sunset(data: dict, weather_data: dict) -> None:
        weather_data.update({"sunset": datetime.fromtimestamp(data['sys']['sunset'])})

    def get_weather(self) -> OpenWeatherData:
        r = self.request()
        result = self.parse_weather(r)
        return result
