from django import forms


class SearchPeminForm(forms.Form):
    q = forms.CharField(max_length=100, required=False)
    sdate = forms.DateField(required=False)
    rdate = forms.DateField(required=False)