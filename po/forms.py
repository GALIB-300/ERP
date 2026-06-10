from django import forms
from .models import Po
from project.models import Project
from resource.models import Resource
from supplier.models import Supplier

class PoForm(forms.ModelForm):
    # Add-bill_amount-as a disabled field (read-only)
    bill_amount = forms.DecimalField(
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
        model = Po
        fields = [
            'project_name_po',
            'po_date',
            'po_no',
            'resource_name_po',
            'resource_unit_po',
            'supplier_name_po',
            'quantity',
            'unit_price',
            'delivery_date',   
        ]

        labels = {
            'project_name_po': 'Project Name',
            'po_date': 'PO Date',
            'po_no': 'PO Number',
            'resource_name_po': 'Resource Name',
            'resource_unit_po': 'Unit',
            'supplier_name_po': 'Supplier Name',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
            'bill_amount': 'Bill Amount',
            'delivery_date': 'Delivery Date',
        }

        widgets = {
            'project_name_po': forms.Select(attrs={'class': 'form-control'}),
            'po_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter po date'
                }
            ),
            'po_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter po number'}),
            'resource_name_po': forms.Select(attrs={'class': 'form-control'}),
            'resource_unit_po': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-fill unit'}),
            'supplier_name_po': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter unit price'}),
            'delivery_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter delivery date'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date fields-(PO date and Delivery date)-convert to-(dd-mm-yyyy) #
        self.fields['po_date'].input_formats = ['%d-%m-%Y']
        self.fields['delivery_date'].input_formats = ['%d-%m-%Y']

        # Project dropdown (Project model) #
        self.fields['project_name_po'].empty_label = "--------- Select Project Name ---------"
        queryset = Project.objects.filter(created_by=user) if user else Project.objects.none()
        self.fields['project_name_po'].queryset = queryset
        self.fields['project_name_po'].label_from_instance = lambda obj: obj.name_of_project

        # Resource dropdown (Resource model) #
        self.fields['resource_name_po'].empty_label = "--------- Select Resource Name ---------"
        queryset = Resource.objects.filter(created_by=user) if user else Resource.objects.none()
        self.fields['resource_name_po'].queryset = queryset
        self.fields['resource_name_po'].label_from_instance = lambda obj: obj.name_of_resource

        # Supplier dropdown (Supplier model) #
        self.fields['supplier_name_po'].empty_label = "--------- Select Supplier Name ---------"
        queryset = Supplier.objects.filter(created_by=user) if user else Supplier.objects.none()
        self.fields['supplier_name_po'].queryset = queryset
        self.fields['supplier_name_po'].label_from_instance = lambda obj: obj.name_of_supplier

        # Pre-fill-bill_amount-from instance (calculated in model.save) #
        self.fields['bill_amount'].initial = getattr(self.instance, "bill_amount", 0)
