from import_export.resources import ModelResource, ValidationError

from .models import (
    InputKoreksi,
)
from masterdata.models import (
    Customer,
)
import datetime


class InputKoreksiResource(ModelResource):
    class Meta:
        model = InputKoreksi
        fields = [
            'id', 'segmen', 'sbf_account', 'bp_number',
            'customer_nm', 'description', 'sid', 'bandwidth',
            'periode', 'amount', 'keterangan', 'sudah_input_ncx',
            'last_order', 'type_last_order', 'status_order',
            'abonemen', 'per_last_biling', 'layanan'
        ]
        export_order = [
            'id', 'segmen', 'sbf_account', 'bp_number',
            'customer_nm', 'description', 'sid', 'bandwidth',
            'periode', 'amount', 'keterangan', 'sudah_input_ncx',
            'last_order', 'type_last_order', 'status_order',
            'abonemen', 'per_last_biling','layanan',
        ]
        skip_unchanged = True
        report_skipped = False

    def before_import_row(self, row, **kwargs):
        if row['id']:
            raise ValidationError(
                'Error field ID must keep blank.'
            )
        row['periode'] = str(int(row['periode']))
        row['sbf_account'] = str(int(row['sbf_account']))
        row['bp_number'] = str(int(row['bp_number']))
        if row['per_last_biling'] == '':
            row['per_last_biling'] = '999901'

        try :
            datetime.datetime.strptime(row['periode'], '%Y%m')
            datetime.datetime.strptime(row['per_last_biling'], '%Y%m')
        except:
            raise ValidationError(
                'Error not valid periode field.'
            )


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
            'customer_nm', 'description', 'sid', 'bandwidth', 'layanan',
            'periode', 'amount', 'keterangan', 'sudah_input_ncx',
            'last_order', 'type_last_order', 'status_order',
            'abonemen', 'per_last_biling', 'error_text',
        ]
        export_order = [
            'segmen', 'sbf_account', 'bp_number',
            'customer_nm', 'description', 'sid', 'bandwidth', 'layanan',
            'periode', 'amount', 'keterangan', 'sudah_input_ncx',
            'last_order', 'type_last_order', 'status_order',
            'abonemen', 'per_last_biling', 'error_text'
        ]
        skip_unchanged = True
        report_skipped = False