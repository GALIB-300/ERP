from django import forms
from .models import Pt
from client.models import Client   

class PtForm(forms.ModelForm):
    # Add-submit_year_pt-as a disabled field (read-only) #
    submit_year_pt = forms.IntegerField(
        required=False,
        label="Submit Year",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = Pt
        fields = [
            'client_name_pt',
            'proposal_information_collect_pt',
            'description_work_pt',
            'total_proposal_pt',
            'prepare_date_pt',
            'submit_date_pt',
            'status_proposal_pt',
            'proposal_award_pt',
        ]
        labels = {
            'client_name_pt': "Client Name",
            'proposal_information_collect_pt': "Proposal Information Source",
            'description_work_pt': "Work Description",
            'total_proposal_pt': "Total Proposal",
            'prepare_date_pt': "Prepare Date",
            'submit_date_pt': "Submit Date",
            'submit_year_pt': "Submit Year",
            'status_proposal_pt': "Status Proposal",
            'proposal_award_pt': "Proposal Award",
        }
        widgets = {
            'client_name_pt': forms.Select(attrs={
                'class': 'form-control',
            }),
            'proposal_information_collect_pt': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description_work_pt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'Enter detailed work description'
            }),
            'total_proposal_pt': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',   # fixed to 1, not editable
                'value': 1
            }),
            'prepare_date_pt': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter prepare date'
                }
            ),
            'submit_date_pt': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter submit date'
                }
            ),
            'status_proposal_pt': forms.Select(attrs={
                'class': 'form-select'
            }),
            'proposal_award_pt': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',   # shows 1 or 0
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date fields-(prepare date and submit date)-convert to-(dd-mm-yyyy) #
        self.fields['prepare_date_pt'].input_formats = ['%d-%m-%Y']
        self.fields['submit_date_pt'].input_formats = ['%d-%m-%Y']

        # Client dropdown (Client model) #
        self.fields['client_name_pt'].empty_label = "--------- Select Client Name ---------"
        queryset = Client.objects.filter(created_by=user) if user else Client.objects.none()
        self.fields['client_name_pt'].queryset = queryset
        self.fields['client_name_pt'].label_from_instance = lambda obj: obj.name_of_client

        # Pre-fill-submit_year_pt-from instance (calculated in model.save) #
        self.fields['submit_year_pt'].initial = getattr(self.instance, "submit_year_pt", 0)
