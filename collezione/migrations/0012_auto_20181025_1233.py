# Generated by Django 2.1.2 on 2018-10-25 12:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('collezione', '0011_auto_20181023_1615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offerta',
            name='moneta',
        ),
        migrations.RemoveField(
            model_name='offerta',
            name='offerente',
        ),
        migrations.RemoveField(
            model_name='offerta',
            name='scambio',
        ),
        migrations.RemoveField(
            model_name='scambio',
            name='contraenti',
        ),
        migrations.RemoveField(
            model_name='scambio',
            name='monete',
        ),
        migrations.AddField(
            model_name='scambio',
            name='monetaControOfferta',
            field=models.ManyToManyField(related_name='monetaControOfferta', to='collezione.Moneta'),
        ),
        migrations.AddField(
            model_name='scambio',
            name='monetaOfferta',
            field=models.ManyToManyField(related_name='monetaOfferta', to='collezione.Moneta'),
        ),
        migrations.AddField(
            model_name='scambio',
            name='offerente',
            field=models.ManyToManyField(related_name='offerente', to='collezione.Utente'),
        ),
        migrations.AddField(
            model_name='scambio',
            name='ricevente',
            field=models.ManyToManyField(related_name='ricevente', to='collezione.Utente'),
        ),
        migrations.AlterField(
            model_name='scambio',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.DeleteModel(
            name='Offerta',
        ),
    ]
