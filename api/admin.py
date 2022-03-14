from django.contrib import admin
from api.models import *


class ModelAdmin(admin.ModelAdmin):
    model = Mark
    list_filter = ["mark"]


class CarImageInline(admin.StackedInline):
    model = CarImage


class CarAdmin(admin.ModelAdmin):
    model = Car
    inlines = [CarImageInline]


class ListItemInline(admin.StackedInline):
    model = ListItem


class ListAdmin(admin.ModelAdmin):
    model = List
    inlines = [ListItemInline]


class SettingsAdmin(admin.ModelAdmin):
    model = Settings
    list_display = ('key', 'value')


admin.site.register(Mark)
admin.site.register(Model, ModelAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Settings, SettingsAdmin)
admin.site.register(List, ListAdmin)
