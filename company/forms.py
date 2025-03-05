from django import forms

from .models import Company


class CompanyForm(forms.ModelForm):
    website_link = forms.URLField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter company website URL: https://",
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = Company
        fields = ["website_link"]
