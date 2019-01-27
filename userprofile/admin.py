from django.contrib import admin

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Profile


class ProfileInline(admin.TabularInline):
    model = Profile
    min = 1
    max = 1


class UserAdminCustom(UserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)