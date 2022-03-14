from django.db import models
import uuid
import os
from jwt_auth.models import Profile
from datetime import date, datetime, timedelta

def get_file_path(instance, filename):
    ext = "jpg"
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('media', filename)


class Mark(models.Model):
    name = models.CharField(max_length=64, verbose_name="Название марки")

    def __str__(self):
        return f"{self.name}"
    

    class Meta:
        verbose_name = "Марка авто"
        verbose_name_plural = "Марки авто"


class Model(models.Model):
    mark = models.ForeignKey(Mark, models.CASCADE, verbose_name="Марка")
    name = models.CharField(max_length=64, verbose_name="Название модели")
    start_year = models.IntegerField(verbose_name="Старт производства")
    end_year = models.IntegerField(blank=True, null=True, verbose_name="Окончание производства")

    def __str__(self):
        return f"{self.mark.name} - {self.name}"
    

    class Meta:
        verbose_name = "Модель авто"
        verbose_name_plural = "Модели авто"


class Car(models.Model):
    views = models.IntegerField(default=0)
    owner = models.ForeignKey(Profile, models.CASCADE, blank=True, null=True)
    city = models.CharField(max_length=64, verbose_name="Город")
    district = models.CharField(max_length=64, null=True, blank=True, verbose_name="Район")
    street = models.CharField(max_length=64, verbose_name="Улица")
    mark = models.CharField(max_length=64, verbose_name="Марка авто")
    model = models.CharField(max_length=64, verbose_name="Модель авто")
    year = models.IntegerField(verbose_name="Год")
    start_date = models.DateField(verbose_name="Начало сдачи")
    end_date = models.DateField(null=True, blank=True, verbose_name="Конец сдачи")
    term = models.CharField(max_length=64, verbose_name="Срок")
    carcase = models.CharField(max_length=64, verbose_name="Кузов")
    _class = models.CharField(max_length=64, verbose_name="Класс")
    price = models.IntegerField(verbose_name="Цена")
    created = models.DateField(verbose_name="Дата создания", default=date.today())
    engine = models.CharField(max_length=64, verbose_name="Двигатель")
    power = models.CharField(max_length=64, verbose_name="Мощность")
    drive = models.CharField(max_length=64, verbose_name="Привод")
    color = models.CharField(max_length=64, verbose_name="Цвет")
    mileage = models.CharField(max_length=64, verbose_name="Пробег")
    rudder = models.CharField(max_length=64, verbose_name="Положение руля")
    free = models.BooleanField(default=False, verbose_name="Бесплатное объявление")
    active_till = models.DateField(verbose_name="Активно до", default=date.today() + timedelta(days=30))
    attached = models.BooleanField(default=False, verbose_name="Прикреплённое объявление")
    boosted_till = models.BooleanField(default=None, verbose_name="Поднято до", null=True, blank=True)

    def __str__(self):
        if self.district:
            district = f" {self.district}"
        else:
            district = ""
        return f"{self.city}{district} {self.street} {self.mark} {self.model} {self.year}"
    

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"


class Favorite(models.Model):
    car = models.ForeignKey(Car, models.CASCADE)
    profile = models.ForeignKey(Profile, models.CASCADE)


class Offer(models.Model):
    car = models.ForeignKey(Car, models.CASCADE)
    profile = models.ForeignKey(Profile, models.CASCADE)
    client = models.ForeignKey(Profile, models.CASCADE, related_name="client")
    date = models.DateField(verbose_name="Дата создания", default=date.today())


class CarImage(models.Model):
    car = models.ForeignKey(Car, models.CASCADE)
    image = models.ImageField(upload_to=get_file_path, verbose_name="Изображение")

    class Meta:
        verbose_name = "Изображение автомобиля"
        verbose_name_plural = "Изображения автомобилей"


class Review(models.Model):
    author = models.ForeignKey(Profile, models.CASCADE, verbose_name="Автор")
    target = models.ForeignKey(Profile, models.CASCADE, related_name="target")
    is_positive = models.BooleanField(verbose_name="Позитивный отзыв")
    text = models.TextField(verbose_name="Текст отзыва")
    created = models.DateField(verbose_name="Дата создания", default=date.today())

    def __str__(self):
        return f"{self.author.first_name} {self.author.last_name} - {self.target.first_name} {self.target.last_name}"


class ChangePasswordTemp(models.Model):
    profile = models.ForeignKey(Profile, models.CASCADE)
    new_password = models.CharField(max_length=500)
    token = models.CharField(max_length=500)
    code = models.CharField(max_length=4)
    confirmation_type = models.CharField(max_length=16)


class Message(models.Model):
    from_profile = models.ForeignKey(Profile, models.CASCADE, related_name="from_profile")
    to_profile = models.ForeignKey(Profile, models.CASCADE)
    text = models.TextField()
    sent = models.DateTimeField(default=datetime.now())


class ChangeEmailTemp(models.Model):
    email = models.CharField(max_length=256)
    profile = models.ForeignKey(Profile, models.CASCADE)
    token = models.CharField(max_length=500)
    code = models.CharField(max_length=4)

class List(models.Model):
    name = models.CharField(max_length=256, verbose_name="название списка", primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Список/категория"
        verbose_name_plural = "Списки и категории"


class ListItem(models.Model):
    list = models.ForeignKey(List, models.CASCADE)
    value = models.CharField(max_length=256, verbose_name="значение")
    
    class Meta:
        verbose_name = "Элемент списка"
        verbose_name_plural = "Элементы списка"


class Payment(models.Model):
    token = models.CharField(max_length=500)
    profile = models.ForeignKey(Profile, models.CASCADE)


class Settings(models.Model):
    key = models.CharField(max_length=256, verbose_name="название настройки", primary_key=True)
    value = models.CharField(max_length=256, verbose_name="значение")

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"


class Deal(models.Model):
    client = models.ManyToManyField(Profile)
    owner = models.ManyToManyField(Profile)
    car = models.ManyToManyField(Car)
    amount = models.IntegerField()
    accepted = models.BooleanField(default=False)