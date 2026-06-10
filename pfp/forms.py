from django import forms
from .models import Pfp
from proposal.models import Proposal

class PfpForm(forms.ModelForm):
    class Meta:
        model = Pfp
        fields = [
            "proposal",
            "title_pfp",
            "submit_to_pfp",
            "submit_by_pfp",
        ]

        labels = {
            "proposal": "Linked Proposal",
            "title_pfp": "Proposal Front Page",
            "submit_to_pfp": "Proposal Submit To",
            "submit_by_pfp": "Proposal Submit By",
        }

        widgets = {
            "title_pfp": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter front page content"
            }),
            "submit_to_pfp": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Enter recipient of proposal"
            }),
            "submit_by_pfp": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Enter sender of proposal"
            }),
        }

    # ✅ Explicitly set queryset for Proposal dropdown
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proposal'].queryset = Proposal.objects.all()
        self.fields['proposal'].widget.attrs.update({
            "class": "form-control"
        })