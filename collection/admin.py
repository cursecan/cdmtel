from django.contrib import admin

from .models import ColTarget

@admin.register(ColTarget)
class ColTargetAdmin(admin.ModelAdmin):
    pass