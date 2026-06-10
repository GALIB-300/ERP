from django import forms
from .models import Letter
from cba.models import Cba   # ✅ adjust if your app name differs

class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = [
            "client_name_letter",
            "wo_no_letter",
            "bill_no_letter",
            "date",
            "recipient_name",
            "recipient_designation",
            "recipient_address",
            "subject",
            "recipient_salutation",
            "body",
            "sender_name",
            "sender_designation",
            "sender_company_name",
            "remarks",
        ]

        labels = {
            "client_name_letter": "Client Name",
            "wo_no_letter": "Work Order No",
            "bill_no_letter": "Bill No",
            "date": "Letter Date",
            "recipient_name": "Recipient Name",
            "recipient_designation": "Recipient Designation",
            "recipient_address": "Recipient Address",
            "subject": "Letter Subject",
            "recipient_salutation": "Recipient Salutation",
            "body": "Letter Body",
            "sender_name": "Sender Name",
            "sender_designation": "Sender Designation",
            "sender_company_name": "Sender Company Name",
            "remarks": "Remarks",
        }

        widgets = {
            "client_name_letter": forms.Select(attrs={"class": "form-control"}),
            "wo_no_letter": forms.Select(attrs={"class": "form-control"}),
            "bill_no_letter": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                format="%d-%m-%Y",
                attrs={
                    "class": "form-control",
                    "type": "text",  # Flatpickr-friendly
                    "placeholder": "Enter date"
                }
            ),
            "recipient_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter recipient name"}),
            "recipient_designation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter recipient designation"}),
            "recipient_address": forms.Textarea(attrs={"class": "form-control", "rows": 1, "placeholder": "Enter recipient address"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter subject line"}),
            "recipient_salutation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter salutation"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Enter main content of the letter"}),
            "sender_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter sender name"}),
            "sender_designation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter sender designation"}),
            "sender_company_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter company name"}),
            "remarks": forms.Textarea(attrs={"class": "form-control", "rows": 1, "placeholder": "Enter remarks (default NA)"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ✅ Date format
        self.fields['date'].input_formats = ['%d-%m-%Y']

        # ✅ Client dropdown (Cba → Ctv chain)
        self.fields['client_name_letter'].empty_label = "--------- Select Client Name ---------"
        queryset = Cba.objects.filter(created_by=user) if user else Cba.objects.none()
        self.fields['client_name_letter'].queryset = queryset
        # adjust depending on your Ctv model fields
        self.fields['client_name_letter'].label_from_instance = (
            lambda obj: obj.client_name_cba.client_name_ctv.client_name_pt
        )

        # ✅ Work Order No dropdown
        self.fields['wo_no_letter'].empty_label = "--------- Select Work Order No ---------"
        queryset = Cba.objects.filter(created_by=user) if user else Cba.objects.none()
        self.fields['wo_no_letter'].queryset = queryset
        self.fields['wo_no_letter'].label_from_instance = lambda obj: obj.wo_no_cba.wo_no_ctv

        # ✅ Bill No dropdown
        self.fields['bill_no_letter'].empty_label = "--------- Select Bill No ---------"
        queryset = Cba.objects.filter(created_by=user) if user else Cba.objects.none()
        self.fields['bill_no_letter'].queryset = queryset
        self.fields['bill_no_letter'].label_from_instance = lambda obj: obj.bill_no_cba