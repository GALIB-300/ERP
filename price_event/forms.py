# A - Import Required Modules #
from django import forms
from .models import ResourcePriceEvent

# B - Form for Resource Price Event #
class ResourcePriceEventForm(forms.ModelForm):
    # Show actual_price as read-only
    actual_price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        label="Actual Price",
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'}
        )
    )

    class Meta:
        model = ResourcePriceEvent
        fields = [
            'resource_name',
            'supplier_name',
            'base_price',
            'increase_decrease_price',
            'effective_from',
        ]
        widgets = {
            'resource_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'increase_decrease_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_from': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }

    # C - Initialization Logic #
    def __init__(self, *args, **kwargs):
        super(ResourcePriceEventForm, self).__init__(*args, **kwargs)
        # Pre-fill actual_price from instance
        self.fields['actual_price'].initial = getattr(self.instance, "actual_price", 0)
