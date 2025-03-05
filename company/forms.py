from django import forms
from .models import CompanyDetails

class CompanyDetailsForm(forms.ModelForm):
    website_link = forms.URLField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter company website URL',
            'class': 'form-control'
        })
    )

    class Meta:
        model = CompanyDetails
        fields = ['website_link']
