# Generated by Django 3.2.9 on 2022-02-24 17:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20220224_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='sent',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 24, 22, 54, 16, 625684)),
        ),
    ]
