from django import forms

from .models import Order


class ResumeOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'order_number'
        ]