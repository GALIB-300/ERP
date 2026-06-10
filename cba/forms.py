from django import forms
from .models import Cba
from ctv.models import Ctv

# ERP-style ModelForm for Cba #
class CbaForm(forms.ModelForm):
    # Disabled read-only field for calculated value #
    actual_bill_amount_cba = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Actual Bill Amount",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = Cba
        fields = [
            "client_name_cba",
            "project_id_cba",
            "wo_no_cba",
            "bill_date_cba",
            "bill_no_cba",
            "bill_amount_cba",
            "vat_ait_cba",
            "vat_ait_amount_cba",
        ]
        labels = {
            "client_name_cba": "Client Name",
            "project_id_cba": "Project ID",
            "wo_no_cba": "Work Order No",
            "bill_date_cba": "Bill Date",
            "bill_no_cba": "Bill No",
            "bill_amount_cba": "Bill Amount",
            "vat_ait_cba": "VAT + AIT",
            "vat_ait_amount_cba": "VAT & AIT Amount",
            "actual_bill_amount_cba": "Actual Bill Amount",
        }
        widgets = {
            "client_name_cba": forms.Select(attrs={"class": "form-control"}),
            "project_id_cba": forms.Select(attrs={"class": "form-control"}),
            "wo_no_cba": forms.Select(attrs={"class": "form-control"}),
            "bill_date_cba": forms.DateInput(
                format='%d-%m-%Y',
                attrs={'class': 'form-control', 'type': 'text', 'placeholder': 'Enter bill date'}
            ),
            "bill_no_cba": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter bill number"
            }),
            "bill_amount_cba": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter bill amount"
            }),
            "vat_ait_cba": forms.Select(attrs={"class": "form-control"}),
            "vat_ait_amount_cba": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter VAT & AIT amount"
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date format #
        self.fields['bill_date_cba'].input_formats = ['%d-%m-%Y']

        # Client dropdown (Ctv model) #
        self.fields['client_name_cba'].empty_label = "--------- Select Client Name ---------"
        queryset = Ctv.objects.filter(created_by=user) if user else Ctv.objects.none()
        self.fields['client_name_cba'].queryset = queryset
        self.fields['client_name_cba'].label_from_instance = lambda obj: obj.client_name_ctv.client_name_pt

        # Project ID dropdown (Ctv model) #
        self.fields['project_id_cba'].empty_label = "--------- Select Project ID ---------"
        queryset = Ctv.objects.filter(created_by=user) if user else Ctv.objects.none()
        self.fields['project_id_cba'].queryset = queryset
        self.fields['project_id_cba'].label_from_instance = lambda obj: obj.project_id_ctv

        # Work Order No dropdown (Ctv model) #
        self.fields['wo_no_cba'].empty_label = "--------- Select Work Order No ---------"
        queryset = Ctv.objects.filter(created_by=user) if user else Ctv.objects.none()
        self.fields['wo_no_cba'].queryset = queryset
        self.fields['wo_no_cba'].label_from_instance = lambda obj: obj.wo_no_ctv

        # Pre-fill disabled calculated field #
        self.fields['actual_bill_amount_cba'].initial = getattr(self.instance, "actual_bill_amount_cba", 0)
