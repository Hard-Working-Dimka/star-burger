# Generated by Django 4.2.20 on 2025-05-01 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_alter_order_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='last_name',
            new_name='lastname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='phone_number',
            new_name='phonenumber',
        ),
    ]
