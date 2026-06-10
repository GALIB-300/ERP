from django import forms
from .models import CustomerDetailed

class CustomerDetailedForm(forms.ModelForm):
    class Meta:
        model = CustomerDetailed
        fields = [
            'name',
            'address',
            'email',
            'phone',
            'company',
        ]

        labels = {
            'name': 'Customer Name',
            'address': 'Address',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'company': 'Company Name',
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
        }
