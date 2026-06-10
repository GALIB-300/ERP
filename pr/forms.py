from django import forms
from .models import Pr
from project.models import Project
from resource.models import Resource

class PrForm(forms.ModelForm):
    class Meta:
        model = Pr
        fields = [
            'project_name_pr',
            'requisition_date_pr',
            'requisition_no_pr',
            'resource_name_pr',
            'resource_unit_pr',
            'quantity_pr',
            'delivery_date_pr',
            'remarks_pr',
        ]

        labels = {
            'project_name_pr': 'Project Name',
            'requisition_date_pr': 'Requisition Date',
            'requisition_no_pr': 'Requisition Number',
            'resource_name_pr': 'Resource Name',
            'resource_unit_pr': 'Resource Unit',
            'quantity_pr': 'Quantity',
            'delivery_date_pr': 'Delivery Date',
            'remarks_pr': 'Remarks',
        }

        widgets = {
            'project_name_pr': forms.Select(attrs={'class': 'form-control'}),
            'requisition_date_pr': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter requisition date'
                }
            ),
            'requisition_no_pr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter requisition number'
            }),
            'resource_name_pr': forms.Select(attrs={'class': 'form-control'}),
            'resource_unit_pr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-fill-Unit',}),
            'quantity_pr': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter quantity',
            }),
            'delivery_date_pr': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter delivery date'
                }
            ),
            'remarks_pr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter remarks'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date fields-(Requisition date & Delivery date)-convert to-(dd-mm-yyyy) #
        self.fields['requisition_date_pr'].input_formats = ['%d-%m-%Y']
        self.fields['delivery_date_pr'].input_formats = ['%d-%m-%Y']

        # Project dropdown (Project model)
        self.fields['project_name_pr'].empty_label = "--------- Select Project Name ---------"
        queryset = Project.objects.filter(created_by=user) if user else Project.objects.none()
        self.fields['project_name_pr'].queryset = queryset
        self.fields['project_name_pr'].label_from_instance = lambda obj: obj.name_of_project

        # Resource dropdown (Resource model)
        self.fields['resource_name_pr'].empty_label = "--------- Select Resource Name ---------"
        queryset = Resource.objects.filter(created_by=user) if user else Resource.objects.none()
        self.fields['resource_name_pr'].queryset = queryset
        self.fields['resource_name_pr'].label_from_instance = lambda obj: obj.name_of_resource