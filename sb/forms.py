# A - Import Required Modules #
from django import forms
from .models import Sb
from po.models import Po   

class SbForm(forms.ModelForm):
    # Add-bill_amount_sb-as a disabled field (read-only)
    bill_amount_sb = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Bill Amount",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = Sb
        fields = [
            'project_name_sb',
            'po_number_sb',
            'resource_name_sb',
            'resource_unit_sb',
            'supplier_name_sb',
            'po_quantity_sb',
            'unit_price_sb',
            'receive_date_sb',
            'actual_receive_quantity_sb',
        ]

        labels = {
            'project_name_sb': 'Project Name',
            'po_number_sb': 'PO Number',
            'resource_name_sb': 'Resource Name',
            'resource_unit_sb': 'Unit',
            'supplier_name_sb': 'Supplier Name',
            'po_quantity_sb': 'Quantity based on PO',
            'unit_price_sb': 'Unit Price',
            'receive_date_sb': 'Receive Date',
            'actual_receive_quantity_sb': 'Actual Receive Quantity',
            'bill_amount_sb': 'Bill Amount',
        }

        widgets = {
            'project_name_sb': forms.Select(attrs={'class': 'form-control'}),
            'po_number_sb': forms.Select(attrs={'class': 'form-control'}),
            'resource_name_sb': forms.Select(attrs={'class': 'form-control'}),
            'resource_unit_sb': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-fill unit'}),
            'supplier_name_sb': forms.Select(attrs={'class': 'form-control'}),
            'po_quantity_sb': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter PO quantity'}),
            'unit_price_sb': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter unit price'}),
            'receive_date_sb': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter receive date'
                }
            ),
            'actual_receive_quantity_sb': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter actual receive quantity'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date fields-(Receive date)-convert to-(dd-mm-yyyy) #
        self.fields['receive_date_sb'].input_formats = ['%d-%m-%Y']

        # Project dropdown (PO model) #
        self.fields['project_name_sb'].empty_label = "--------- Select Project Name ---------"
        queryset = Po.objects.filter(created_by=user) if user else Po.objects.none()
        self.fields['project_name_sb'].queryset = queryset
        self.fields['project_name_sb'].label_from_instance = lambda obj: obj.project_name_po

        # PO Number dropdown (PO model) #
        self.fields['po_number_sb'].empty_label = "--------- Select PO Number ---------"
        queryset = Po.objects.filter(created_by=user) if user else Po.objects.none()
        self.fields['po_number_sb'].queryset = queryset
        self.fields['po_number_sb'].label_from_instance = lambda obj: obj.po_no

        # Resource dropdown (PO model) #
        self.fields['resource_name_sb'].empty_label = "--------- Select Resource Name ---------"
        queryset = Po.objects.filter(created_by=user) if user else Po.objects.none()
        self.fields['resource_name_sb'].queryset = queryset
        self.fields['resource_name_sb'].label_from_instance = lambda obj: obj.resource_name_po

        # Supplier dropdown (PO model) #
        self.fields['supplier_name_sb'].empty_label = "--------- Select Supplier Name ---------"
        queryset = Po.objects.filter(created_by=user) if user else Po.objects.none()
        self.fields['supplier_name_sb'].queryset = queryset
        self.fields['supplier_name_sb'].label_from_instance = lambda obj: obj.supplier_name_po

        # Pre-fill-bill_amount_sb-from instance (calculated in model.save) #
        self.fields['bill_amount_sb'].initial = getattr(self.instance, "bill_amount_sb", 0)