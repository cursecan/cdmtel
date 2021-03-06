from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import (
    InputKoreksi,  
    DocumentImportTemplate,  
)
from .resources import (
    InputKoreksiResource,
)

@admin.register(InputKoreksi)
class InputKoreksiAdmin(ImportExportModelAdmin):
    resource_class = InputKoreksiResource


@admin.register(DocumentImportTemplate)
class DocumentImportTemplate(admin.ModelAdmin):
    pass