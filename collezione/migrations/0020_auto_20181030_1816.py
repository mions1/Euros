# Generated by Django 2.1.2 on 2018-10-30 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collezione', '0019_auto_20181030_1815'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scambio',
            name='votoOfferente',
        ),
        migrations.RemoveField(
            model_name='scambio',
            name='votoRicevente',
        ),
    ]
