from django import forms
from .models import Rbp, Project, Resource, Supplier

# Form for Resource Base Price (RBP) #
class RbpForm(forms.ModelForm):
    # Add-actual_base_price-as a disabled field (read-only)
    actual_base_price = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Actual Base Price",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = Rbp
        fields = [
            'project_name_rbp',
            'resource_name_rbp',
            'resource_unit_rbp',
            'supplier_name_rbp',
            'price_select_date',
            'resource_base_price',
            'resource_discount_price',
        ]

        labels = {
            'project_name_rbp': 'Project Name',
            'resource_name_rbp': 'Resource Name',
            'resource_unit_rbp': 'Unit',
            'supplier_name_rbp': 'Supplier Name',
            'price_select_date': 'Price Select Date',
            'resource_base_price': 'Base Price',
            'resource_discount_price': 'Discount Price',
            'actual_base_price': 'Actual Base Price',
        }

        widgets = {
            'project_name_rbp': forms.Select(attrs={'class': 'form-control'}),
            'resource_name_rbp': forms.Select(attrs={'class': 'form-control'}),
            'resource_unit_rbp': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
            }),
            'supplier_name_rbp': forms.Select(attrs={'class': 'form-control'}),
            'price_select_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'price_select_date': forms.DateInput(
    format='%d-%m-%Y',
    attrs={
        'class': 'form-control',
        'type': 'text',              # text so Flatpickr controls display
        'id': 'id_price_select_date', # important for Flatpickr hook
        'placeholder': 'Enter price select date',
        'autocomplete': 'off'
    }
),
            'resource_discount_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discount price',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date field format (dd-mm-yyyy) #
        self.fields['price_select_date'].input_formats = ['%d-%m-%Y']

        # Project dropdown #
        self.fields['project_name_rbp'].empty_label = "--------- Select Project Name ---------"
        if user:
            queryset = Project.objects.filter(created_by=user)
        else:
            queryset = Project.objects.none()
        if self.instance.pk and self.instance.project_name_rbp:
            selected = Project.objects.filter(pk=self.instance.project_name_rbp.pk)
            queryset = (queryset | selected).distinct()
        self.fields['project_name_rbp'].queryset = queryset

        # Resource dropdown #
        self.fields['resource_name_rbp'].empty_label = "--------- Select Resource Name ---------"
        if user:
            queryset = Resource.objects.filter(created_by=user)
        else:
            queryset = Resource.objects.none()
        if self.instance.pk and self.instance.resource_name_rbp:
            selected = Resource.objects.filter(pk=self.instance.resource_name_rbp.pk)
            queryset = (queryset | selected).distinct()
        self.fields['resource_name_rbp'].queryset = queryset

        # Supplier dropdown #
        self.fields['supplier_name_rbp'].empty_label = "--------- Select Supplier Name ---------"
        if user:
            queryset = Supplier.objects.filter(created_by=user)
        else:
            queryset = Supplier.objects.none()
        if self.instance.pk and self.instance.supplier_name_rbp:
            selected = Supplier.objects.filter(pk=self.instance.supplier_name_rbp.pk)
            queryset = (queryset | selected).distinct()
        self.fields['supplier_name_rbp'].queryset = queryset

        # Pre-fill-actual_base_price-from instance (calculated in model.save) #
        self.fields['actual_base_price'].initial = getattr(self.instance, "actual_base_price", 0)
