from import_export.resources import ModelResource

from .models import (
    InputKoreksi,
)
from masterdata.models import (
    Customer,
)


class InputKoreksiResource(ModelResource):
    class Meta:
        model = InputKoreksi
        fields = [
            'id', 'segmen', 'sbf_account', 'bp_number',
            'customer_nm', 'description', 'sid', 'wb',
            'periode', 'amount', 'keterangan', 'sudah_input_ncx',
            'last_order', 'type_last_order', 'status_order',
            'abonemen', 'per_last_biling',
        ]
        export_order = [
            'id', 'segmen', 'sbf_account', 'bp_number',
            'customer_nm', 'description', 'sid', 'wb',
            'periode', 'amount', 'keterangan', 'sudah_input_ncx',
            'last_order', 'type_last_order', 'status_order',
            'abonemen', 'per_last_biling',
        ]
        skip_unchanged = True
        report_skipped = False

    def after_save_instance(self, instance, using_transactions, dry_run):
        objs = Customer.objects.filter(account_number=instance.sbf_account)
        instance.state = InputKoreksi.INVALID
        if not objs.exists():
            instance.error_text = 'Customer number not found'
        else :
            obj = objs.get()
            if instance.amount > obj.get_saldo():
                instance.error_text = 'Amount koreksi must lower than current billing'
            
            else:
                instance.customer_obj = obj
                instance.state = InputKoreksi.VALID
        
        instance.save()

class ExportKoreksiResource(ModelResource):
    class Meta:
        model = InputKoreksi
        fields = [
            'segmen', 'sbf_account', 'bp_number',
            'customer_nm', 'description', 'sid', 'wb',
            'periode', 'amount', 'keterangan', 'sudah_input_ncx',
            'last_order', 'type_last_order', 'status_order',
            'abonemen', 'per_last_biling', 'error_text',
        ]
        export_order = [
            'segmen', 'sbf_account', 'bp_number',
            'customer_nm', 'description', 'sid', 'wb',
            'periode', 'amount', 'keterangan', 'sudah_input_ncx',
            'last_order', 'type_last_order', 'status_order',
            'abonemen', 'per_last_biling', 'error_text'
        ]
        skip_unchanged = True
        report_skipped = False