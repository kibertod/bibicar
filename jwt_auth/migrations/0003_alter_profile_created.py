# Generated by Django 3.2.7 on 2022-02-20 08:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jwt_auth', '0002_alter_profile_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='created',
            field=models.DateField(default=datetime.date(2022, 2, 20), verbose_name='Дата регистрации'),
        ),
    ]