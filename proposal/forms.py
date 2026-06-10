from django import forms
from .models import Proposal

class ProposalForm(forms.ModelForm):
   # Add-submit_year-as a disabled field (read-only) #
    submit_year = forms.IntegerField(
        required=False,
        label="Submit Year",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = Proposal
        fields = [
            'proposal_prepare_date',
            'proposal_no',
            'customer_name_proposal',
            'description_of_proposal',
            'proposal_submit_date',
            'submit_by',
            'proposal_amount',

        ]

        labels = {
            'proposal_prepare_date': 'Proposal Prepare Date',
            'proposal_no': 'Proposal Number',
            'customer_name_proposal': 'Customer Name',
            'description_of_proposal': 'Description',
            'proposal_submit_date': 'Proposal Submit Date',
            'submit_year': 'Submit Year',
            'submit_by': 'Submit By',
            'proposal_amount': 'Proposal Amount',
        }

        widgets = {
            'proposal_prepare_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter proposal prepare date'
                }
            ),
            'proposal_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter proposal number'}),
            'customer_name_proposal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer number'}),
            'description_of_proposal': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 1}),
            'proposal_submit_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'class': 'form-control',
                    'type': 'text',  # text so Flatpickr controls display
                    'placeholder': 'Enter proposal submit date'
                }
            ),
            'submit_by': forms.Select(attrs={'class': 'form-control'}),
            'proposal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter proposal amount',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Date fields-(Proposal prepare date and Proposal submit date)-convert to-(dd-mm-yyyy) #
        self.fields['proposal_prepare_date'].input_formats = ['%d-%m-%Y']
        self.fields['proposal_submit_date'].input_formats = ['%d-%m-%Y']

        # Pre-fill-submit_year-from instance (calculated in model.save) #
        self.fields['submit_year'].initial = getattr(self.instance, "submit_year", 0)
