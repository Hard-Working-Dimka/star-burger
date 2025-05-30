# Generated by Django 4.2.20 on 2025-05-13 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocoordapp', '0002_alter_place_unique_together_alter_place_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='lat',
            field=models.FloatField(blank=True, null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='place',
            name='lon',
            field=models.FloatField(blank=True, null=True, verbose_name='Долгота'),
        ),
    ]
