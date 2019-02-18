from django import forms

from .models import Order
from cdmsoro.models import PermintaanResume

class ResumeOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'circuit',
            'order_number'
        ]


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
