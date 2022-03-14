from django.contrib import admin
from jwt_auth.models import *


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    search_fields  = ('first_name', 'last_name','email', 'phone')
    list_display  = ('first_name', 'last_name','email', 'phone')


admin.site.register(Profile, ProfileAdmin)
