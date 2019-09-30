from django.contrib import admin

from user.models import UserConfig


class UserConfigAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = [field.name for field in UserConfig._meta.get_fields()]

admin.site.register(UserConfig, UserConfigAdmin)