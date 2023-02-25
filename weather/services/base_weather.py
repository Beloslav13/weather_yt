from dataclasses import dataclass
from typing import Protocol, TypeAlias


Celsius: TypeAlias = int


@dataclass(slots=True, frozen=True)
class Coordinate:
    latitude: float
    longitude: float


class Weather(Protocol):

    def get_weather(self):
        pass


class WeatherStorage(Protocol):

    def save(self) -> None:
        pass


def save_weather(storage: WeatherStorage) -> None:
    storage.save()
