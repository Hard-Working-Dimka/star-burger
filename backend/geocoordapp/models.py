from django.db import models


class Place(models.Model):
    address = models.CharField(max_length=256, verbose_name='Адрес', unique=True, )
    lon = models.FloatField(verbose_name='Долгота', blank=True, null=True, )
    lat = models.FloatField(verbose_name='Широта', blank=True, null=True, )
    request = models.TimeField(auto_now=True, verbose_name='Запрос к API', )

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'
