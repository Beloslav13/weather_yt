from django.db import models


class Weather(models.Model):
    city = models.CharField(max_length=50, verbose_name="Город")
    temperature = models.IntegerField(verbose_name="Температура")

    class Meta:
        abstract = True


class LogWeather(models.Model):
    date = models.DateTimeField(verbose_name="Дата запроса")
    result = models.BooleanField(default=False, verbose_name="Результат запроса")

    class Meta:
        abstract = True


class OpenWeather(Weather):

    class Meta:
        verbose_name = "Погода OpenWeather"
        verbose_name_plural = "Погода OpenWeather"

    open_error = models.OneToOneField("OpenWeatherLog", on_delete=models.CASCADE, related_name="weather")
    latitude = models.FloatField(verbose_name="Ширина")
    longitude = models.FloatField(verbose_name="Долгота")
    sunrise = models.DateTimeField(verbose_name="Восход")
    sunset = models.DateTimeField(verbose_name="Закат")


class OpenWeatherLog(LogWeather):

    class Meta:
        verbose_name = "Лог OpenWeather"
        verbose_name_plural = "Логи OpenWeather"

    error = models.JSONField(verbose_name="Ошибка", default=dict, blank=True, null=True)
