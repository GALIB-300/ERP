from django import forms
from .models import Rwc
from project.models import Project   # ✅ Import Project

class RwcForm(forms.ModelForm):
    class Meta:
        model = Rwc
        fields = ['company', 'requisition_date', 'requisition_no', 'project_name_rwc', 'delivery_date']
        labels = {
            'company': 'Select Company',
            'requisition_date': 'Requisition Date',
            'requisition_no': 'Requisition No',
            'project_name_rwc': 'Project Name',
            'delivery_date': 'Delivery Date',
        }
        widgets = {
            'company': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Choose company'
            }),
            'requisition_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'id': 'id_requisition_date',   # ✅ for Flatpickr
                    'type': 'text',
                    'placeholder': 'Enter requisition date'
                }
            ),
            'requisition_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto / Manual Entry'
            }),
            'project_name_rwc': forms.Select(attrs={
                'class': 'form-control'
            }),
            'delivery_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'id': 'id_delivery_date',   # ✅ for Flatpickr
                    'type': 'text',
                    'placeholder': 'Enter delivery date'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ✅ Date field formats
        self.fields['requisition_date'].input_formats = ['%d-%m-%Y']
        self.fields['delivery_date'].input_formats = ['%d-%m-%Y']

        # ✅ Project dropdown
        self.fields['project_name_rwc'].empty_label = "--------- Select Project Name ---------"
        if user:
            queryset = Project.objects.filter(created_by=user)
        else:
            queryset = Project.objects.none()
        if self.instance.pk and self.instance.project_name_rwc:
            selected = Project.objects.filter(pk=self.instance.project_name_rwc.pk)
            queryset = (queryset | selected).distinct()
        self.fields['project_name_rwc'].queryset = queryset

        # ✅ Make requisition_no read-only when editing existing record
        if self.instance and self.instance.pk:
            self.fields['requisition_no'].widget.attrs['readonly'] = True
