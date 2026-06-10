from django.db import models
from django.contrib.auth.models import User   # Built-in User model
from project.models import Project   # <-- import Project here
import math

MM_TO_FT = 0.003281  # conversion factor (mm → ft)

# Role list for casting app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users #
class CastingProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='casting_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in casting operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Casting Role Profile"
        verbose_name_plural = "Casting Role Profiles"

# Casting Model #
class Casting(models.Model):
    TYPE_CASTING = [
        ('manual', 'Manual'),
        ('rmc', 'RMC'),
    ]

    RATIO_SUM = [
        ('0', ''),       # empty label for "0"
        ('5.5', '5.5'),
        ('7', '7'),
        ('10', '10'),
    ]

    DESIGN_CEMENT = [
        ('0%', '0%'),
        ('100%', '100%'),
    ]

    DESIGN_SYLHET_SAND = [
        ('0%', '0%'),
        ('100%', '100%'),
        ('75%', 'Three-quarter strength'),
        ('50%', 'Half strength'),
        ('25%', 'Quarter strength'),
    ]

    DESIGN_LOCAL_SAND = [
        ('0%', '0%'),
        ('100%', '100%'),
        ('75%', 'Three-quarter strength'),
        ('50%', 'Half strength'),
        ('25%', 'Quarter strength'),
    ]

    DESIGN_STONE_20mm = [
        ('0%', '0%'),
        ('100%', '100%'),
        ('75%', 'Three-quarter strength'),
        ('50%', 'Half strength'),
        ('25%', 'Quarter strength'),
    ]

    DESIGN_STONE_16mm = [
        ('0%', '0%'),
        ('100%', '100%'),
        ('75%', 'Three-quarter strength'),
        ('50%', 'Half strength'),
        ('25%', 'Quarter strength'),
    ]

    DESIGN_STONE_12mm = [
        ('0%', '0%'),
        ('100%', '100%'),
        ('75%', 'Three-quarter strength'),
        ('50%', 'Half strength'),
        ('25%', 'Quarter strength'),
    ]

    project_name_casting = models.ForeignKey(
    Project,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='casting_project_name_casting',
    verbose_name="Project Name"
)
    location = models.CharField(max_length=100, default="NA")
    component_name = models.CharField(max_length=100, default="NA")
    component_id = models.CharField(max_length=50, default="NA")

    # Cylindrical #
    pai_cb = models.FloatField(default=math.pi)
    radius_cb_mm = models.FloatField(default=0)
    height_cb_mm = models.FloatField(default=0)
    number_cb = models.IntegerField(default=0)

    # Square/Rectangle #
    length_sb_mm = models.FloatField(default=0)
    breadth_sb_mm = models.FloatField(default=0)
    height_sb_mm = models.FloatField(default=0)
    number_sb = models.IntegerField(default=0)

    # Triangle #
    base_tb_mm = models.FloatField(default=0)
    perpendicular_tb_mm = models.FloatField(default=0)
    height_tb_mm = models.FloatField(default=0)
    number_tb = models.IntegerField(default=0)

    # Trapezoid #
    length1_trb_mm = models.FloatField(default=0)
    length2_trb_mm = models.FloatField(default=0)
    breadth_trb_mm = models.FloatField(default=0)
    height_trb_mm = models.FloatField(default=0)
    number_trb = models.IntegerField(default=0)

    # Deduct Quantity #
    location_dq = models.CharField(max_length=100, default="NA")
    component_name_dq = models.CharField(max_length=100, default="NA")
    component_id_dq = models.CharField(max_length=50, default="NA")
    length_dq_mm = models.FloatField(default=0)
    breadth_dq_mm = models.FloatField(default=0)
    height_dq_mm = models.FloatField(default=0)
    number_dq = models.IntegerField(default=0)

    # Calculated fields-based on-(Actual Quantity & Quantity with Dry Volume) #
    actual_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Calculation in Model"
    )
    quantity_with_dry_volume = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Calculation in Model"
    )

    type_casting = models.CharField(
        max_length=20,
        choices=TYPE_CASTING,
        default='manual',
        help_text="Defines casting type"
    )

    # Calculated fields-based on-(Casting-RMC & Casting-Manual) #
    casting_rmc = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto show casting_rmc"
    )
    casting_manual = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto show casting_manual"
    )

    ratio_sum_a = models.CharField(
        max_length=20,
        choices=RATIO_SUM,
        default='0',
        help_text="Defines the ratio sum a"
    )
    ratio_sum_b = models.CharField(
        max_length=20,
        choices=RATIO_SUM,
        default='0',
        help_text="Defines the ratio sum b"
    )
    ratio_sum_c = models.CharField(
        max_length=20,
        choices=RATIO_SUM,
        default='0',
        help_text="Defines the ratio sum c"
    )

    cement_design = models.CharField(
        max_length=20,
        choices=DESIGN_CEMENT,
        default='0%',
        help_text="Defines the cement design ratio"
    )
    sylhet_sand_design = models.CharField(
        max_length=20,
        choices=DESIGN_SYLHET_SAND,
        default='0%',
        help_text="Defines the Sylhet sand design ratio"
    )
    local_sand_design = models.CharField(
        max_length=20,
        choices=DESIGN_LOCAL_SAND,
        default='0%',
        help_text="Defines the local sand design ratio"
    )
    stone_20mm_design = models.CharField(
        max_length=20,
        choices=DESIGN_STONE_20mm,
        default='0%',
        help_text="Defines the 20mm stone design ratio"
    )
    stone_16mm_design = models.CharField(
        max_length=20,
        choices=DESIGN_STONE_16mm,
        default='0%',
        help_text="Defines the 16mm stone design ratio"
    )
    stone_12mm_design = models.CharField(
        max_length=20,
        choices=DESIGN_STONE_12mm,
        default='0%',
        help_text="Defines the 12mm stone design ratio"
    )

    cement = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto show cement weight"
    )
    sylhet_sand = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto show sylhet sand weight"
    )
    local_sand = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto show local sand weight"
    )
    stone_20mm = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto show stone 20mm weight"
    )

    stone_16mm = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto show stone 16mm weight"
    )

    stone_12mm = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto show stone 12mm weight"
    )

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this casting"
    )

    # Link wp to the user (Manager Construction) #
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="castings",
        verbose_name="Manager Construction",
        null=True,
        blank=True
    )

    # ERP compulsory audit fields #
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="castings_created",
        verbose_name="Created By",
        help_text="User who created this casting record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="castings_updated",
        verbose_name="Updated By",
        help_text="User who last updated this casting record"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created",
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated",
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = "Casting"
        verbose_name_plural = "Castings"

     # --- Calculation Methods --- #
def quantity_cb(self):
    if self.radius_cb_mm and self.height_cb_mm:
        return self.pai_cb * ((self.radius_cb_mm * MM_TO_FT) ** 2) * (self.height_cb_mm * MM_TO_FT) * self.number_cb
    return 0

def quantity_sb(self):
    if self.length_sb_mm and self.breadth_sb_mm and self.height_sb_mm:
        return (self.length_sb_mm * MM_TO_FT) * (self.breadth_sb_mm * MM_TO_FT) * (self.height_sb_mm * MM_TO_FT) * self.number_sb
    return 0

def quantity_tb(self):
    if self.base_tb_mm and self.perpendicular_tb_mm and self.height_tb_mm:
        return 0.5 * (self.base_tb_mm * MM_TO_FT) * (self.perpendicular_tb_mm * MM_TO_FT) * (self.height_tb_mm * MM_TO_FT) * self.number_tb
    return 0

def quantity_trb(self):
    if self.length1_trb_mm and self.length2_trb_mm and self.breadth_trb_mm and self.height_trb_mm:
        return (((self.length1_trb_mm * MM_TO_FT) + (self.length2_trb_mm * MM_TO_FT)) / 2) * (self.breadth_trb_mm * MM_TO_FT) * (self.height_trb_mm * MM_TO_FT) * self.number_trb
    return 0

def quantity_dq(self):
    if self.length_dq_mm and self.breadth_dq_mm and self.height_dq_mm:
        return (self.length_dq_mm * MM_TO_FT) * (self.breadth_dq_mm * MM_TO_FT) * (self.height_dq_mm * MM_TO_FT) * self.number_dq
    return 0

def total_quantity(self):
    return self.quantity_cb() + self.quantity_sb() + self.quantity_tb() + self.quantity_trb()

def actual_quantity_calc(self):
    return self.total_quantity() - self.quantity_dq()

def quantity_with_dry_volume_calc(self):
    return self.actual_quantity_calc() * 1.5

# --- Helper to convert design % string to float --- #
def _design_to_float(self, design_str):
    try:
        return float(str(design_str).strip('%')) / 100.0
    except (ValueError, TypeError):
        return 0.0

# --- Material Calculations with Zero Checks --- #
def cement_calc(self):
    if not self.ratio_sum_a or float(self.ratio_sum_a) == 0:
        return 0
    return (self.quantity_with_dry_volume_calc() / float(self.ratio_sum_a)) * self._design_to_float(self.cement_design)

def sylhet_sand_calc(self):
    if not self.ratio_sum_b or float(self.ratio_sum_b) == 0:
        return 0
    return (self.quantity_with_dry_volume_calc() / float(self.ratio_sum_b)) * self._design_to_float(self.sylhet_sand_design)

def local_sand_calc(self):
    if not self.ratio_sum_c or float(self.ratio_sum_c) == 0:
        return 0
    return (self.quantity_with_dry_volume_calc() / float(self.ratio_sum_c)) * self._design_to_float(self.local_sand_design)

def stone_20mm_calc(self):
    if not self.ratio_sum_a or float(self.ratio_sum_a) == 0:
        return 0
    return (self.quantity_with_dry_volume_calc() / float(self.ratio_sum_a)) * self._design_to_float(self.stone_20mm_design)

def stone_16mm_calc(self):
    if not self.ratio_sum_b or float(self.ratio_sum_b) == 0:
        return 0
    return (self.quantity_with_dry_volume_calc() / float(self.ratio_sum_b)) * self._design_to_float(self.stone_16mm_design)

def stone_12mm_calc(self):
    if not self.ratio_sum_c or float(self.ratio_sum_c) == 0:
        return 0
    return (self.quantity_with_dry_volume_calc() / float(self.ratio_sum_c)) * self._design_to_float(self.stone_12mm_design)

def save(self, *args, **kwargs):
    # Calculated-Casting RMC & Casting Manual #
    self.actual_quantity = self.actual_quantity_calc()
    self.quantity_with_dry_volume = self.quantity_with_dry_volume_calc()
    self.casting_rmc = self.actual_quantity
    self.casting_manual = self.quantity_with_dry_volume

    # Material calculations #
    self.cement = self.cement_calc()
    self.sylhet_sand = self.sylhet_sand_calc()
    self.local_sand = self.local_sand_calc()
    self.stone_20mm = self.stone_20mm_calc()
    self.stone_16mm = self.stone_16mm_calc()
    self.stone_12mm = self.stone_12mm_calc()

    super().save(*args, **kwargs)

def __str__(self):
    return f"Estimate #{self.id} - Actual Quantity: {self.actual_quantity_calc():.2f} ft³"

