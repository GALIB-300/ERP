from django import forms
from .models import Casting, Project

class CastingForm(forms.ModelForm):
    # Disabled fields
    actual_quantity = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Actual Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    quantity_with_dry_volume = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Quantity with dry volume",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    casting_rmc = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Casting RMC",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    casting_manual = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Casting Manual",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    cement = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Cement",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    sylhet_sand = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Sylhet Sand",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    local_sand = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Local Sand",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    stone_20mm = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Stone 20mm",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    stone_16mm = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Stone 16mm",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    stone_12mm = forms.DecimalField(
        max_digits=14, decimal_places=2, required=False,
        label="Stone 12mm",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)   # safely remove 'user'
        super().__init__(*args, **kwargs)

        # Project dropdown
        self.fields['project_name_casting'].empty_label = "--------- Select Project Name ---------"
        if user and hasattr(Project, 'created_by'):
            queryset = Project.objects.filter(created_by=user)
        else:
            queryset = Project.objects.all()

        # Keep selected project available when editing
        if self.instance.pk and self.instance.project_name_casting:
            selected = Project.objects.filter(pk=self.instance.project_name_casting.pk)
            queryset = (queryset | selected).distinct()

        self.fields['project_name_casting'].queryset = queryset

        # Pre-fill calculated fields from instance
        self.fields['actual_quantity'].initial = getattr(self.instance, "actual_quantity", 0)
        self.fields['quantity_with_dry_volume'].initial = getattr(self.instance, "quantity_with_dry_volume", 0)
        self.fields['casting_rmc'].initial = getattr(self.instance, "casting_rmc", 0)
        self.fields['casting_manual'].initial = getattr(self.instance, "casting_manual", 0)
        self.fields['cement'].initial = getattr(self.instance, "cement", 0)
        self.fields['sylhet_sand'].initial = getattr(self.instance, "sylhet_sand", 0)
        self.fields['local_sand'].initial = getattr(self.instance, "local_sand", 0)
        self.fields['stone_20mm'].initial = getattr(self.instance, "stone_20mm", 0)
        self.fields['stone_16mm'].initial = getattr(self.instance, "stone_16mm", 0)
        self.fields['stone_12mm'].initial = getattr(self.instance, "stone_12mm", 0)

    class Meta:
        model = Casting
        fields = [
            'project_name_casting',
            'location',
            'component_name',
            'component_id',

            # Cylindrical #
            "radius_cb_mm", "height_cb_mm", "number_cb",

            # Square/Rectangle #
            "length_sb_mm", "breadth_sb_mm", "height_sb_mm", "number_sb",

            # Triangle #
            "base_tb_mm", "perpendicular_tb_mm", "height_tb_mm", "number_tb",

            # Trapezoid #
            "length1_trb_mm", "length2_trb_mm", "breadth_trb_mm", "height_trb_mm", "number_trb",

            # Deduct Quantity #
            "location_dq", "component_name_dq", "component_id_dq",
            "length_dq_mm", "breadth_dq_mm", "height_dq_mm", "number_dq",

            'type_casting',
            'ratio_sum_a',
            'ratio_sum_b',
            'ratio_sum_c',
            'cement_design',
            'sylhet_sand_design',
            'local_sand_design',
            'stone_20mm_design',
            'stone_16mm_design',
            'stone_12mm_design',
        ]

        labels = {
            'project_name_casting': 'Project Name',
            'location': 'Location',
            'component_name': 'Component Name',
            'component_id': 'Component ID',

            # Cylindrical #
            "radius_cb_mm": "Radius (mm)",
            "height_cb_mm": "Height (mm)",
            "number_cb": "Quantity",

            # Square/Rectangle #
            "length_sb_mm": "Length (mm)",
            "breadth_sb_mm": "Breadth (mm)",
            "height_sb_mm": "Height (mm)",
            "number_sb": "Quantity",

            # Triangle #
            "base_tb_mm": "Base (mm)",
            "perpendicular_tb_mm": "Perpendicular (mm)",
            "height_tb_mm": "Height (mm)",
            "number_tb": "Quantity",

            # Trapezoid #
            "length1_trb_mm": "Length 1 (mm)",
            "length2_trb_mm": "Length 2 (mm)",
            "breadth_trb_mm": "Breadth (mm)",
            "height_trb_mm": "Height (mm)",
            "number_trb": "Quantity",

            # Deduct Quantity #
            "location_dq": "Deduct Quantity Location",
            "component_name_dq": "Deduct Quantity Name",
            "component_id_dq": "Deduct Quantity Component ID",
            "length_dq_mm": "Length (mm)",
            "breadth_dq_mm": "Breadth (mm)",
            "height_dq_mm": "Height (mm)",
            "number_dq": "Quantity",

            'actual_quantity': 'Actual Quantity',
            'quantity_with_dry_volume': 'Quantity with Dry Volume',
            'type_casting': 'Type of Casting',
            'casting_rmc': 'Casting RMC',
            'casting_manual': 'Casting Manual',
            'ratio_sum_a': 'Ratio Sum-A',
            'ratio_sum_b': 'Ratio Sum-B',
            'ratio_sum_c': 'Ratio Sum-C',
            'cement_design': 'Cement Design',
            'sylhet_sand_design': 'Sylhet Sand Design',
            'local_sand_design': 'Local Sand Design',
            'stone_20mm_design': 'Stone 20mm Design',
            'stone_16mm_design': 'Stone 16mm Design',
            'stone_12mm_design': 'Stone 12mm Design',
            'cement': 'Cement',
            'sylhet_sand': 'Sylhet Sand',
            'local_sand': 'Local Sand',
            'stone_20mm': 'Stone 20mm',
            'stone_16mm': 'Stone 16mm',
            'stone_12mm': 'Stone 12mm',
        }

widgets = {
    'project_name_casting': forms.Select(attrs={'class': 'form-control'}),
    'location': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
    'component_name': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter component name'}),
    'component_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter component id'}),

    # Cylindrical #
    "radius_cb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "height_cb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "number_cb": forms.NumberInput(attrs={"class": "form-control"}),

    # Square/Rectangle #
    "length_sb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "breadth_sb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "height_sb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "number_sb": forms.NumberInput(attrs={"class": "form-control"}),

    # Triangle #
    "base_tb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "perpendicular_tb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "height_tb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "number_tb": forms.NumberInput(attrs={"class": "form-control"}),

    # Trapezoid #
    "length1_trb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "length2_trb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "breadth_trb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "height_trb_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "number_trb": forms.NumberInput(attrs={"class": "form-control"}),

    # Deduct Quantity #
    "location_dq": forms.TextInput(attrs={"class": "form-control"}),
    "component_name_dq": forms.TextInput(attrs={"class": "form-control"}),
    "component_id_dq": forms.TextInput(attrs={"class": "form-control"}),
    "length_dq_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "breadth_dq_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "height_dq_mm": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
    "number_dq": forms.NumberInput(attrs={"class": "form-control"}),

    'type_casting': forms.Select(attrs={'class': 'form-control'}),
    'ratio_sum_a': forms.Select(attrs={'class': 'form-control'}),
    'ratio_sum_b': forms.Select(attrs={'class': 'form-control'}),
    'ratio_sum_c': forms.Select(attrs={'class': 'form-control'}),

    'cement_design': forms.Select(attrs={"class": "form-control"}),
    'sylhet_sand_design': forms.Select(attrs={"class": "form-control"}),
    'local_sand_design': forms.Select(attrs={"class": "form-control"}),
    'stone_20mm_design': forms.Select(attrs={"class": "form-control"}),
    'stone_16mm_design': forms.Select(attrs={"class": "form-control"}),
    'stone_12mm_design': forms.Select(attrs={"class": "form-control"}),
}

def clean(self):
    cleaned_data = super().clean()
    if cleaned_data.get("radius_cb_mm") == 0 or cleaned_data.get("height_cb_mm") == 0:
        raise ValidationError("Radius and height must be greater than zero.")
    return cleaned_data

