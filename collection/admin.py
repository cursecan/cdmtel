from django.contrib import admin

from .models import (
    ColTarget, Saldo, AvidenttargetCol, ColSegment
)

@admin.register(ColTarget)
class ColTargetAdmin(admin.ModelAdmin):
    pass

@admin.register(Saldo)
class SaldoAdmin(admin.ModelAdmin):
    pass

@admin.register(AvidenttargetCol)
class AvidenttargetColAdmin(admin.ModelAdmin):
    pass

@admin.register(ColSegment)
class ColSegmentAdmin(admin.ModelAdmin):
    pass