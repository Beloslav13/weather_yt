import os
from datetime import datetime
from typing import NamedTuple

from django.utils import timezone
from weather.services.base_weather import Celsius, Coordinate

from weather.models import OpenWeatherLog, OpenWeather

# test data
data = {'coord': {'lon': 36.56731, 'lat': 50.556},
        'weather': [{'id': 800, 'main': 'Clear', 'description': 'ясно', 'icon': '01d'}], 'base': 'stations',
        'main': {'temp': -7.88, 'feels_like': -14.77, 'temp_min': -8.28, 'temp_max': -7.88, 'pressure': 1022,
                 'humidity': 62}, 'visibility': 10000, 'wind': {'speed': 5, 'deg': 320}, 'clouds': {'all': 0},
        'dt': 1677153668, 'sys': {'type': 1, 'id': 9030, 'country': 'RU', 'sunrise': 1677126678, 'sunset': 1677164602},
        'timezone': 10800, 'id': 824987, 'name': 'Gorod Belgorod', 'cod': 200}

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

    def save(self):
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

    def request(self):
        # try:
            # response = requests.get(url=self.url).json()
        # except JSONDecodeError as e:
        #     print(e)
        # except ConnectionError as e:
        #     print(e)
        # except Exception as e:
        #     print(e)
        return data

    def parse_weather(self, response: dict) -> OpenWeatherData:
        city = self.get_city(response)
        coordinate = self.get_coordinate(response['coord'])
        temp = self.get_temperature(response)
        sunrise = self.get_sunrise(response)
        sunset = self.get_sunset(response)
        return OpenWeatherData(
            log=LogOpenWeatherData(date=timezone.now(), result=True, error={}),
            city=city,
            temp=temp,
            latitude=coordinate.latitude,
            longitude=coordinate.longitude,
            sunrise=sunrise,
            sunset=sunset,
        )

    @staticmethod
    def get_city(data: dict) -> str:
        return data['name']

    @staticmethod
    def get_coordinate(data: dict) -> Coordinate:
        coordinate = Coordinate(data['lat'], data['lon'])
        return coordinate

    @staticmethod
    def get_temperature(data: dict) -> Celsius:
        temp = data['main']['temp']
        return Celsius(temp)

    @staticmethod
    def get_sunrise(data: dict) -> datetime:
        return datetime.fromtimestamp(data['sys']['sunrise'])

    @staticmethod
    def get_sunset(data: dict) -> datetime:
        return datetime.fromtimestamp(data['sys']['sunset'])

    def get_weather(self) -> OpenWeatherData:
        r = self.request()
        result = self.parse_weather(r)
        return result
