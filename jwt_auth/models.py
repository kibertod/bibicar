from django.db import models
import uuid
from datetime import date
import os


def get_file_path(instance, filename):
    ext = "jpg"
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('media', filename)


class Profile(models.Model):
    created = models.DateField(default=date.today(), verbose_name="Дата регистрации")
    license = models.CharField(max_length=500, blank=True, null=True, verbose_name="Водительское удостоверение")
    password = models.CharField(max_length=500, verbose_name="Хэш пароля")
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True, verbose_name="Аватар")
    phone = models.CharField(max_length=12, blank=True, null=True, verbose_name="Номер телефона")
    email = models.CharField(max_length=128, blank=True, null=True, verbose_name="Электронная почта")
    passport = models.CharField(max_length=128, blank=True, null=True, verbose_name="Пасспортные данные")
    first_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Отчество")
    need_relogin = models.BooleanField(default=False, verbose_name="Нужна повторная авторизация")
    vk_id = models.CharField(max_length=64, blank=True, null=True)
    fb_id = models.CharField(max_length=64, blank=True, null=True)
    blocked = models.BooleanField(default=False, verbose_name="Заблокирован")
    vip_till = models.DateField(default=None, verbose_name="V.I.P. подписка до", blank=True, null=True)
    park = models.BooleanField(default=False, verbose_name="Автопарк")
    balance = models.IntegerField(default=0, verbose_name="Баланс")
    ads = models.IntegerField(default=2, verbose_name="Баланс объявлений")


    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
    

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email} {self.phone}"


class SessionToken(models.Model):
    profile = models.ForeignKey(Profile, models.CASCADE)
    token = models.CharField(max_length=500)
    refresh = models.CharField(max_length=500)


class OldToken(models.Model):
    token = models.CharField(max_length=500)


class VkIntegrationTemp(models.Model):
    token = models.CharField(max_length=500)
    profile = models.ForeignKey(Profile, models.CASCADE, null=True, blank=True)


class FacebookIntegrationTemp(models.Model):
    token = models.CharField(max_length=500)
    profile = models.ForeignKey(Profile, models.CASCADE, null=True, blank=True)


class RegTemp(models.Model):
    phone = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    email_notification = models.BooleanField(default=False)
    phone_notification = models.BooleanField(default=False)
    password = models.CharField(max_length=500, verbose_name="Хэш пароля")
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True, verbose_name="Аватар")
    phone = models.CharField(max_length=12, blank=True, null=True, verbose_name="Номер телефона")
    passport = models.CharField(max_length=128, blank=True, null=True, verbose_name="Пасспортные данные")
    first_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Отчество")
    token = models.CharField(max_length=500)
    code = models.CharField(max_length=4)


class EmailAuthTemp(models.Model):
    email = models.CharField(max_length=128)
    token = models.CharField(max_length=500)
    code = models.CharField(max_length=4)
