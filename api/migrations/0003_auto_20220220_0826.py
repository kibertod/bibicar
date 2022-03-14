# Generated by Django 3.2.7 on 2022-02-20 08:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20220219_0843'),
    ]

    operations = [
        migrations.RenameField(
            model_name='car',
            old_name='mildeage',
            new_name='mileage',
        ),
        migrations.AlterField(
            model_name='car',
            name='created',
            field=models.DateField(default=datetime.date(2022, 2, 20), verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='message',
            name='sent',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 20, 8, 26, 7, 298325)),
        ),
        migrations.AlterField(
            model_name='offer',
            name='date',
            field=models.DateField(default=datetime.date(2022, 2, 20), verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='review',
            name='created',
            field=models.DateField(default=datetime.date(2022, 2, 20), verbose_name='Дата создания'),
        ),
    ]
