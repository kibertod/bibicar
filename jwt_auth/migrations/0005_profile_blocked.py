# Generated by Django 3.2.9 on 2022-02-24 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jwt_auth', '0004_alter_profile_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='blocked',
            field=models.BooleanField(default=False, verbose_name='Заблокирован'),
        ),
    ]