from django import forms

from cdmsoro.validators import validate_file_extension, validate_file_size

from .models import (
    ColTarget, AvidenttargetCol
)
from masterdata.models import Customer


class ColTargetForm(forms.ModelForm):
    class Meta:
        model = ColTarget
        fields = [
            'amount',
            'due_date'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD'})
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 1:
            raise forms.ValidationError('Value must greater than 0.')
        return amount


CustomerColFormet = forms.inlineformset_factory(Customer, ColTarget, form=ColTargetForm, extra=1, max_num=20)


class AvidenttargetColForm(forms.ModelForm):
    class Meta:
        model = AvidenttargetCol
        fields = [
            'doc'
        ]