from django import forms

from .models import (
    PermintaanResume, Validation
)
from masterdata.models import Circuit

class BukisForm(forms.Form):
    pic = forms.CharField(max_length=15, required=True)
    circuit = forms.CharField(max_length=30, required=True)
    message = forms.CharField(widget=forms.Textarea)
    avident = forms.FileField(max_length=200, required=True)


    def clean_circuit(self):
        circuit = self.cleaned_data['circuit']
        circuit_objs = Circuit.objects.filter(
            sid=circuit, is_active=False
        )

        if not circuit_objs.exists():
            raise forms.ValidationError('Link tidak ditemukan atau tidak terisolir.')


        circuit_obj = circuit_objs.get()
        permintaan_obj = PermintaanResume.objects.filter(
            sid = circuit_obj, suspend = circuit_obj.get_last_order()
        )
        if permintaan_obj.exists():
            raise forms.ValidationError('Permintaan buka isolir pada SID ini telah di request.')
        
        return circuit

    
class BukisValidationForm(forms.ModelForm):
    class Meta:
        model = Validation
        fields = [
            'action',
            'message'
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4})
        }


class UpdateBukisForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(), required=True)
    doc = forms.FileField(required=True)