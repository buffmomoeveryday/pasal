from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.user.models import CustomUser
from .models import CustomUser


class UserAdmin(BaseUserAdmin):
    model = CustomUser
    ordering = ["email"]


admin.site.register(CustomUser)
