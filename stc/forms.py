from django import forms
from .models import Stc
from project.models import Project
from supplier.models import Supplier

class StcForm(forms.ModelForm):
    class Meta:
        model = Stc
        fields = [
            'project_name_stc',
            'supplier_name_stc',
            'po_date_stc',
            'po_no_stc',
            'vat_ait_stc',
            'delivery_term_stc',
            'payment_term_stc',
            'warranty_term_stc',
        ]

        labels = {
            'project_name_stc': 'Project Name',
            'supplier_name_stc': 'Supplier Name',
            'po_date_stc': 'PO Date',
            'po_no_stc': 'PO Number',
            'vat_ait_stc': 'VAT/AIT',
            'delivery_term_stc': 'Delivery Term',
            'payment_term_stc': 'Payment Term',
            'warranty_term_stc': 'Warranty Term',
        }

        widgets = {
            'project_name_stc': forms.Select(attrs={'class': 'form-control'}),
            'supplier_name_stc': forms.Select(attrs={'class': 'form-control'}),
            'po_date_stc': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter PO date'
                }
            ),
            'po_no_stc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PO number'}),
            'vat_ait_stc': forms.Select(attrs={'class': 'form-control'}),
            'delivery_term_stc': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter delivery terms', 'rows': 1}),
            'payment_term_stc': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter payment terms', 'rows': 2}),
            'warranty_term_stc': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter warranty terms', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date field-(PO date-STC)-convert to-(dd-mm-yyyy) #
        self.fields['po_date_stc'].input_formats = ['%d-%m-%Y']

        # Project dropdown (Project model) #
        self.fields['project_name_stc'].empty_label = "--------- Select Project Name ---------"
        queryset = Project.objects.filter(created_by=user) if user else Project.objects.none()
        self.fields['project_name_stc'].queryset = queryset
        self.fields['project_name_stc'].label_from_instance = lambda obj: obj.name_of_project

        # Supplier dropdown (Supplier model) #
        self.fields['supplier_name_stc'].empty_label = "--------- Select Supplier Name ---------"
        queryset = Supplier.objects.filter(created_by=user) if user else Supplier.objects.none()
        self.fields['supplier_name_stc'].queryset = queryset
        self.fields['supplier_name_stc'].label_from_instance = lambda obj: obj.name_of_supplier
