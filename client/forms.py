from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'name_of_client',
            'client_address',
            'contact_person_name',
            'contact_person_number',
        ]

        labels = {
            'name_of_client': 'Client Name',
            'client_address': 'Client Address',
            'contact_person_name': 'Contact Person Name',
            'contact_person_number': 'Contact Person Number',
        }

        widgets = {
            'name_of_client': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter client name'
            }),
            'client_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter client address'
            }),
            'contact_person_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name'
            }),
            'contact_person_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),
        }
