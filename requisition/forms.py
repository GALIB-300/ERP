from django import forms
from .models import Requisition, Project, Resource

class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = [
            'project_name_requisition',
            'requisition_date',
            'requisition_no',
            'resource_name_requisition',
            'resource_unit_requisition',
            'quantity',
            'delivery_date',
            'remarks',
            'status',   # 👈 include status
        ]

        labels = {
            'project_name_requisition': 'Project Name',
            'requisition_date': 'Requisition Date',
            'requisition_no': 'Requisition Number',
            'resource_name_requisition': 'Resource Name',
            'resource_unit_requisition': 'Unit',
            'quantity': 'Quantity',
            'delivery_date': 'Delivery Date',
            'remarks': 'Remarks',
            'status': 'Approval Status',   # 👈 label for dropdown
        }

        widgets = {
            'project_name_requisition': forms.Select(attrs={'class': 'form-control'}),
            'requisition_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter requisition date'
                }
            ),
            'requisition_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter requisition number'}),
            'resource_name_requisition': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter resource'}),
            'resource_unit_requisition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-fill unit'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),
            'delivery_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'placeholder': 'Enter delivery date'
                }
            ),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter remarks'}),
            'status': forms.Select(attrs={'class': 'form-control'}),   # 👈 dropdown widget
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date fields-(Requisition date & Delivery date)-convert to-(dd-mm-yyyy) #
        self.fields['requisition_date'].input_formats = ['%d-%m-%Y']
        self.fields['delivery_date'].input_formats = ['%d-%m-%Y']

        # Project dropdown #
        self.fields['project_name_requisition'].empty_label = "--------- Select Project Name ---------"
        if user:
            queryset = Project.objects.filter(created_by=user)
        else:
            queryset = Project.objects.none()
        if self.instance.pk and self.instance.project_name_requisition:
            selected = Project.objects.filter(pk=self.instance.project_name_requisition.pk)
            queryset = (queryset | selected).distinct()
        self.fields['project_name_requisition'].queryset = queryset

        # Resource dropdown #
        self.fields['resource_name_requisition'].empty_label = "--------- Select Resource Name ---------"
        if user:
            queryset = Resource.objects.filter(created_by=user)
        else:
            queryset = Resource.objects.none()
        if self.instance.pk and self.instance.resource_name_requisition:
            selected = Resource.objects.filter(pk=self.instance.resource_name_requisition.pk)
            queryset = (queryset | selected).distinct()
        self.fields['resource_name_requisition'].queryset = queryset
