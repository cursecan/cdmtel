from import_export import resources
from import_export.widgets import ForeignKeyWidget

from .models import ManualOrderSoro
from masterdata.models import Circuit

class ManualOrderSoroResource(resources.ModelResource):
    sid = resources.Field(attribute='sid', column_name='sid', widget=ForeignKeyWidget(Circuit, 'sid'))

    class Meta:
        model = ManualOrderSoro
        fields = [
            'id',
            'sid',
            'order_type',
            'keterangan',
        ]
        export_order = [
            'id',
            'sid',
            'order_type',
            'keterangan',
        ]
        # import_id_fields = ['sid']
        skip_unchanged = True
        report_skipped = False
