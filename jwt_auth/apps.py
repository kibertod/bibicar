from tabnanny import verbose
from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jwt_auth'
    verbose_name = "Пользователи"