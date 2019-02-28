from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (
    PermintaanResume, UpdatePermintaan,
    Validation, Avident, ManualOrderSoro
)

from .resources import ManualOrderSoroResource

@admin.register(PermintaanResume)
class PermintaanResumeAdmin(admin.ModelAdmin):
    pass

@admin.register(UpdatePermintaan)
class PermintaanResumeAdmin(admin.ModelAdmin):
    pass

@admin.register(Validation)
class PermintaanResumeAdmin(admin.ModelAdmin):
    pass


@admin.register(Avident)
class AvidentAdmin(admin.ModelAdmin):
    pass

@admin.register(ManualOrderSoro)
class ManualOrderSoro(ImportExportModelAdmin):
    list_display = [
        'order_number', 'sid', 'keterangan', 'timestamp'
    ]
    resource_class = ManualOrderSoroResource
    