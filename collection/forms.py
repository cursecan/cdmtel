from django import forms
from django.db.models import F, Q, Sum, Value as V
from django.db.models.functions import Coalesce
from django.forms import BaseInlineFormSet

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
            'due_date': forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD'}),
            'amount': forms.NumberInput(attrs={'class':'c_nominal'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount < 1:
            raise forms.ValidationError('Value must greater than 0.')
        return amount

class CustomColFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        t = 0
        for form in self.forms:
            t += form.cleaned_data.get('amount', 0)
        if t != self.instance.cur_saldo:
            raise forms.ValidationError('Total termin tidak sama dengan saldo sistem.')

CustomerColFormet = forms.inlineformset_factory(Customer, ColTarget, form=ColTargetForm, formset=CustomColFormset, extra=1)


class AvidenttargetColForm(forms.ModelForm):
    class Meta:
        model = AvidenttargetCol
        fields = [
            'doc',
        ]