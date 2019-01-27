from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import (
    Customer, Circuit, Order
)
from .resources import (
    CustomerResource, CircuitResource, OrderResource
)

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
        'order_number', 'type_order', 'status', 'create_by'
    ]
    list_per_page = 50
    list_filter = [
        'status'
    ]
    search_fields = [
        'order_number'
    ]


# class Order(CommonBase):
#     RESUME = 'RO'
#     SUSPEND = 'SO'
#     TYPE_LIST = (
#         (SUSPEND, 'SUSPEND'),
#         (RESUME, 'RESUME')
#     )
#     order_number = models.CharField(max_length=13, unique=True)
#     type_order = models.CharField(max_length=2, choices=TYPE_LIST, default=SUSPEND)
#     circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.order_number