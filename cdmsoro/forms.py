from django import forms

from .validators import validate_file_extension, validate_file_size

from .models import (
    PermintaanResume, Validation, ManualOrder
)
from masterdata.models import Circuit

class BukisForm(forms.Form):
    pic = forms.CharField(
        max_length=100, required=True, 
        widget=forms.TextInput(
            attrs={
                'placeholder': '@telegram_username'
            }
        )
    )
    circuit = forms.CharField(max_length=30, required=True)
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Alasan buka isolir...',
                'rows': 4
            }
        )
    )
    avident = forms.FileField(max_length=200, required=True, validators=[validate_file_extension, validate_file_size])


    def clean_circuit(self):
        circuit = self.cleaned_data['circuit']
        circuit_objs = Circuit.objects.filter(
            sid=circuit, is_active=False
        )

        if not circuit_objs.exists():
            raise forms.ValidationError('Link masih aktif tidak ada isolir.')


        circuit_obj = circuit_objs.get()
        permintaan_obj = PermintaanResume.objects.filter(
            sid = circuit_obj, suspend = circuit_obj.get_last_order()
        )
        if permintaan_obj.exists():
            raise forms.ValidationError('Duplikat request permintaan buka isolir.')
        
        return circuit

    def clean_pic(self):
        pic = self.cleaned_data['pic']
        if pic[0] != '@':
            raise forms.ValidationError('Username telegram harus diawali "@"')
        return pic

    
class BukisValidationForm(forms.ModelForm):
    class Meta:
        model = Validation
        fields = [
            'action',
            'message'
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Approved!'})
        }

        def clean_message(self):
            msg =  self.cleaned_data['message']
            if msg is None or msg == '':
                msg = 'Approved!'
            return msg


class UpdateBukisForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'placeholder': 'Message...'}), required=True)
    # doc = forms.FileField(required=True, validators=[validate_file_extension, validate_file_size])


class UploadDocForm(forms.Form):
    doc = forms.FileField(required=True, validators=[validate_file_extension, validate_file_size])

class ManualOrderForm(forms.ModelForm):
    class Meta:
        model = ManualOrder
        fields = [
            'permintaan_resume',
            'message'
        ]
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4, 'placeholder': 'Ket. error penyebab manual...'
            })
        }

    def __init__(self, per_resume, *args, **kwargs):
        super(ManualOrderForm, self).__init__(*args, **kwargs)
        self.fields['permintaan_resume'].queryset = PermintaanResume.objects.filter(pk=per_resume)