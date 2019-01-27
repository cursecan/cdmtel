from django.contrib.auth.models import User

from import_export import resources
from import_export.widgets import ForeignKeyWidget

from .models import (
    Customer, Circuit, Order
)

class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer
        fields = ['account_number']
        import_id_fields = ['account_number']
        skip_unchanged = True
        report_skipped = False

class CircuitResource(resources.ModelResource):
    account = resources.Field(attribute='account', column_name='account', widget=ForeignKeyWidget(Customer, 'account_number'))
    class Meta:
        model = Circuit
        fields = ['sid', 'account', 'is_active']
        export_order = ['sid', 'account', 'is_active']
        import_id_fields = ['sid']
        skip_unchanged = True
        report_skipped = False


class OrderResource(resources.ModelResource):
    circuit = resources.Field(attribute='circuit', column_name='circuit', widget=ForeignKeyWidget(Circuit, 'sid'))
    create_by = resources.Field(attribute='create_by', column_name='create_by', widget=ForeignKeyWidget(User, 'username'))
    class Meta:
        model = Order
        fields = [
            'order_number', 'type_order',
            'status', 'circuit', 'create_by'
        ]
        export_order = [
            'order_number', 'type_order',
            'status', 'circuit', 'create_by'
        ]
        import_id_fields = ['order_number']
        skip_unchanged = True
        report_skipped = False