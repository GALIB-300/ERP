from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            'name_of_resource',
            'unit',
            'resource_group',   # ✅ lowercase, matches model
        ]

        labels = {
            'name_of_resource': 'Resource Name',
            'unit': 'Unit',
            'resource_group': 'Resource Group',
        }

        widgets = {
            'name_of_resource': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter resource name'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-control',
            }),
            'resource_group': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


