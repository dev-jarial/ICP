import os

from django import forms

from .models import Company, CompanyUpload


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


class CompanyUploadForm(forms.ModelForm):
    class Meta:
        model = CompanyUpload
        fields = ["file"]

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        if uploaded_file:
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            allowed_extensions = [".csv", ".xlsx"]

            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    "Only CSV or Excel (.xlsx) files are allowed."
                )

        return uploaded_file


class CompanySearchForm(forms.Form):
    company_search_query = forms.CharField(
        widget=forms.Textarea, label="Search Company"
    )
