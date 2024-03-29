# Generated by Django 3.2.7 on 2022-02-18 16:23

import datetime
from django.db import migrations, models
import django.db.models.deletion
import jwt_auth.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAuthTemp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=128)),
                ('token', models.CharField(max_length=500)),
                ('code', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='OldToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(default=datetime.date(2022, 2, 18), verbose_name='Дата регистрации')),
                ('license', models.CharField(blank=True, max_length=500, null=True, verbose_name='Водительское удостоверение')),
                ('password', models.CharField(max_length=500, verbose_name='Хэш пароля')),
                ('image', models.ImageField(blank=True, null=True, upload_to=jwt_auth.models.get_file_path, verbose_name='Аватар')),
                ('phone', models.CharField(blank=True, max_length=12, null=True, verbose_name='Номер телефона')),
                ('email', models.CharField(blank=True, max_length=128, null=True, verbose_name='Электронная почта')),
                ('passport', models.CharField(blank=True, max_length=128, null=True, verbose_name='Пасспортные данные')),
                ('first_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Фамилия')),
                ('middle_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Отчество')),
                ('need_relogin', models.BooleanField(default=False, verbose_name='Нужна повторная авторизация')),
                ('vk_id', models.CharField(blank=True, max_length=64, null=True)),
                ('fb_id', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='RegTemp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=128)),
                ('email_notification', models.BooleanField(default=False)),
                ('phone_notification', models.BooleanField(default=False)),
                ('password', models.CharField(max_length=500, verbose_name='Хэш пароля')),
                ('image', models.ImageField(blank=True, null=True, upload_to=jwt_auth.models.get_file_path, verbose_name='Аватар')),
                ('phone', models.CharField(blank=True, max_length=12, null=True, verbose_name='Номер телефона')),
                ('passport', models.CharField(blank=True, max_length=128, null=True, verbose_name='Пасспортные данные')),
                ('first_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Фамилия')),
                ('middle_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Отчество')),
                ('token', models.CharField(max_length=500)),
                ('code', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='VkIntegrationTemp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=500)),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jwt_auth.profile')),
            ],
        ),
        migrations.CreateModel(
            name='SessionToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=500)),
                ('refresh', models.CharField(max_length=500)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jwt_auth.profile')),
            ],
        ),
        migrations.CreateModel(
            name='FacebookIntegrationTemp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=500)),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jwt_auth.profile')),
            ],
        ),
    ]
