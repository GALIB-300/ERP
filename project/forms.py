from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name_of_project',
            'project_address',
            'contact_person_name',
            'contact_person_number',
        ]

        labels = {
            'name_of_project': 'Project Name',
            'project_address': 'Project Address',
            'contact_person_name': 'Contact Person Name',
            'contact_person_number': 'Contact Person Number',
        }

        widgets = {
            'name_of_project': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'project_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project address'
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
