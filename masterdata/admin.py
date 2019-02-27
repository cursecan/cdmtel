from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import (
    Customer, Circuit, Order, Segment
)
from .resources import (
    CustomerResource, CircuitResource, OrderResource
)


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class = CustomerResource
    search_fields = [
        'account_number'
    ]


@admin.register(Circuit)
class CircuitAdmin(ImportExportModelAdmin):
    resource_class = CircuitResource
    search_fields = [
        'sid'
    ]


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource
    list_display = [
        'get_sid', 'get_account',
        'order_number', 'type_order', 'status', 'create_by'
    ]
    list_per_page = 50
    list_filter = [
        'status'
    ]
    search_fields = [
        'order_number', 'circuit__sid', 'circuit__account__account_number'
    ]
