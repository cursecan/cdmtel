from django import forms

from .models import (
    Order, Circuit
)
from cdmsoro.models import PermintaanResume

class ResumeOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'circuit',
            'order_number'
        ]

    def __init__(self, sid, bks_id, *args, **kwargs):
        super(ResumeOrderForm, self).__init__(*args, **kwargs)
        self.fields['circuit'].queryset = Circuit.objects.filter(sid=sid)
        self.bks = bks_id

    def clean_order_number(self):
        order_n = self.cleaned_data['order_number']
        if order_n[:2] != '1-':
            raise forms.ValidationError('Order not in format 1-*')
        return order_n

    def clean_circuit(self):
        cisr_obj = self.cleaned_data['circuit']

        permin_obj = cisr_obj.permin_bukis.filter(validate=True, closed=False)
        if not permin_obj.exists():
            raise forms.ValidationError('Unvalidate circuit.')

        if self.bks != permin_obj.latest('timestamp').id:
            raise forms.ValidationError('Unmatch bukis order.')

        return cisr_obj

class ResumeOrderForm_v2(forms.Form):
    circuit = forms.IntegerField(required=False)
    order_number = forms.CharField(required=True)

    def clean_circuit(self):
        circuit = self.cleaned_data.get('circuit')
        obj_re = PermintaanResume.objects.get(pk=circuit)
        print(obj_re.is_approved())
        if obj_re.is_approved():
            raise forms.ValidationError('Permitaan belum mendapat approval.')
        return circuit


class CreateResumeOrderForm(forms.Form):
    permin_bukis = forms.IntegerField(required=True)
    resume_order = forms.CharField(max_length=30, required=True)

    def clean_resume_order(self):
        order_num = self.cleaned_data['resume_order']
        if order_num[:2] != '1-':
            raise forms.ValidationError('Order number not valid.')

        if Order.objects.filter(order_number=order_num).exists():
            raise forms.validators('Duplicate order cannot process.')

        return order_num


    def clean_permin_bukis(self):
        bukis_id = self.cleaned_data['permin_bukis']
        permin_obj = PermintaanResume.objects.get(pk=bukis_id)

        if not permin_obj.validate:
            raise forms.ValidationError('Permintaan belum validasi approval.')

        return bukis_id