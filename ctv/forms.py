# A - Import Required Modules #
from django import forms
from .models import Ctv
from pt.models import Pt

# B - ERP-style ModelForm for Ctv #
class CtvForm(forms.ModelForm):
    # Disabled read-only fields for calculated values #
    vat_ait_amount_ctv = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="VAT & AIT Amount",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )
    actual_contract_value_ctv = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Actual Contract Value",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = Ctv
        fields = [
            "client_name_ctv",
            "project_id_ctv",
            "wo_no_ctv",
            "description_work_ctv",
            "start_date_ctv",
            "finish_date_ctv",
            "contract_value_ctv",
            "vat_ait_ctv",
            "vat_ctv",
            "ait_ctv",
        ]
        labels = {
            "client_name_ctv": "Client Name",
            "project_id_ctv": "Project ID",
            "wo_no_ctv": "Work Order No",
            "description_work_ctv": "Work Description",
            "start_date_ctv": "Start Date",
            "finish_date_ctv": "Finish Date",
            "contract_value_ctv": "Contract Value",
            "vat_ait_ctv": "VAT + AIT",
            "vat_ctv": "VAT",
            "ait_ctv": "AIT",
            "vat_ait_amount_ctv": "VAT & AIT Amount",
            "actual_contract_value_ctv": "Actual Contract Value",
        }
        widgets = {
            "client_name_ctv": forms.Select(attrs={"class": "form-control"}),
            "project_id_ctv": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter project ID"
            }),
            "wo_no_ctv": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter work order number"
            }),
            "description_work_ctv": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 1,
                "placeholder": "Enter detailed work description"
            }),
            "start_date_ctv": forms.DateInput(
                format='%d-%m-%Y',
                attrs={'class': 'form-control', 'type': 'text', 'placeholder': 'Enter start date'}
            ),
            "finish_date_ctv": forms.DateInput(
                format='%d-%m-%Y',
                attrs={'class': 'form-control', 'type': 'text', 'placeholder': 'Enter finish date'}
            ),
            "contract_value_ctv": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter contract value"
            }),
            "vat_ait_ctv": forms.Select(attrs={"class": "form-control"}),
            "vat_ctv": forms.Select(attrs={"class": "form-control"}),
            "ait_ctv": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date formats #
        self.fields['start_date_ctv'].input_formats = ['%d-%m-%Y']
        self.fields['finish_date_ctv'].input_formats = ['%d-%m-%Y']

        # Filter dropdown to only show Awarded clients #
        self.fields['client_name_ctv'].empty_label = "--------- Select Client Name ---------"
        queryset = Pt.objects.filter(proposal_award_pt=1)
        self.fields['client_name_ctv'].queryset = queryset
        self.fields['client_name_ctv'].label_from_instance = lambda obj: obj.client_name_pt

        # Pre-fill disabled calculated fields #
        self.fields['vat_ait_amount_ctv'].initial = getattr(self.instance, "vat_ait_amount_ctv", 0)
        self.fields['actual_contract_value_ctv'].initial = getattr(self.instance, "actual_contract_value_ctv", 0)