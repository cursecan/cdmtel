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

    def __init__(self, sid, *args, **kwargs):
        super(ResumeOrderForm, self).__init__(*args, **kwargs)
        self.fields['circuit'].queryset = Circuit.objects.filter(sid=sid)

    def clean_order_number(self):
        order_n = self.cleaned_data['order_number']
        if order_n[:2] != '1-':
            raise forms.ValidationError('Order not in format 1-*')
        return order_n


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
