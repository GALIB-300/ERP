# A - Import Required Modules #
from django import forms
from django.db.models import Q
from .models import Rip
from rbp.models import Rbp

# B - Form for Resource Increase Price (RIP) #
class RipForm(forms.ModelForm):
    # C - Add actual_base_price as a disabled field (read-only)
    actual_base_price_rip = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Actual Base Price",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )

    # D - Meta configuration #
    class Meta:
        model = Rip
        fields = [
            'project_resource_supplier_name_rip',
            'project_name_rip',
            'resource_name_rip',
            'resource_unit_rip',
            'supplier_name_rip',
            'base_price_rip',
            'increase_decrease_price_rip',
            'effective_from',
        ]

        labels = {
            'project_resource_supplier_name_rip': 'Project & Resource & Supplier Name',
            'project_name_rip': 'Project Name',
            'resource_name_rip': 'Resource Name',
            'resource_unit_rip': 'Resource Unit',
            'supplier_name_rip': 'Supplier Name',
            'base_price_rip': 'Resource Base Price',
            'increase_decrease_price_rip': 'Resource Increase/Decrease Price',
            'actual_base_price_rip': 'Resource Actual Base Price',
            'effective_from': 'Effective From',
        }

        widgets = {
            'project_resource_supplier_name_rip': forms.Select(attrs={'class': 'form-control'}),
            'project_name_rip': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'resource_name_rip': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'resource_unit_rip': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'supplier_name_rip': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'base_price_rip': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'id': 'id_base_price_rip',
            }),
            'increase_decrease_price_rip': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter increase/decrease amount',
            }),
            'effective_from': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',        # text so Flatpickr controls display
                    'id': 'id_effective_from',
                    'placeholder': 'Enter effective from date',
                    'autocomplete': 'off'
                }
            ),
        }

    # E - Initialization logic #
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date field format (dd-mm-yyyy)
        self.fields['effective_from'].input_formats = ['%d-%m-%Y', '%Y-%m-%d']

        # Project & Resource & Supplier Dropdown
        self.fields['project_resource_supplier_name_rip'].empty_label = "--------- Select Project & Resource & Supplier Name ---------"
        if self.instance and self.instance.pk:
            self.fields['project_resource_supplier_name_rip'].queryset = Rbp.objects.filter(
                Q(created_by=user) | Q(pk=self.instance.project_resource_supplier_name_rip.pk)
            )
        else:
            self.fields['project_resource_supplier_name_rip'].queryset = Rbp.objects.filter(created_by=user)

        self.fields['project_resource_supplier_name_rip'].label_from_instance = (
            lambda obj: f"{obj.project_name_rbp} | {obj.resource_name_rbp} | {obj.supplier_name_rbp}"
        )

        # Pre-fill actual_base_price_rip from instance
        self.fields['actual_base_price_rip'].initial = getattr(self.instance, "actual_base_price_rip", 0)

    