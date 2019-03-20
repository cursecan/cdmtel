from django.contrib import admin

from .models import (
    ColTarget, Saldo, AvidenttargetCol, ColSegment, Validation
)

@admin.register(Validation)
class ValidationAdmin(admin.ModelAdmin):
    pass

@admin.register(ColTarget)
class ColTargetAdmin(admin.ModelAdmin):
    pass

@admin.register(Saldo)
class SaldoAdmin(admin.ModelAdmin):
    search_fields = [
        'customer__account_number', 'timestamp'
    ]
    list_display = [
        'customer', 'amount'
    ]

@admin.register(AvidenttargetCol)
class AvidenttargetColAdmin(admin.ModelAdmin):
    pass

@admin.register(ColSegment)
class ColSegmentAdmin(admin.ModelAdmin):
    pass