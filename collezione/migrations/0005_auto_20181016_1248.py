# Generated by Django 2.1.2 on 2018-10-16 12:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collezione', '0004_auto_20181016_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utente',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
