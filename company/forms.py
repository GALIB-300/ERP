from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'company_name',
            'company_address',
            'company_email',
            'company_contact_no',
        ]

        labels = {
            'company_name': 'Company Name',
            'company_address': 'Company Address',
            'company_email': 'Company Email',
            'company_contact_no': 'Company Contact Number',
        }

        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
            'company_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company address'
            }),
            'company_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company email'
            }),
            'company_contact_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company contact number'
            }),
        }
