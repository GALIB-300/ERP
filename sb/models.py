# A - Import Required Modules #
from django.db import models
from django.contrib.auth.models import User   

# Role list for sb app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users #
class SbProfile(models.Model):
    user = models.OneToOneField(
        User,   
        on_delete=models.CASCADE,
        related_name='sb_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in sb operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "SB Role Profile"
        verbose_name_plural = "SB Role Profiles"

# SB Model #
class Sb(models.Model):
    project_name_sb = models.ForeignKey(
        'po.PO',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sb_project_name_sb',
        verbose_name="Project Name"
    )
    po_number_sb = models.ForeignKey(
        'po.PO',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sb_po_number_sb',
        verbose_name="PO Number"
    )
    resource_name_sb = models.ForeignKey(
        'po.PO',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sb_resource_name_sb',
        verbose_name="Resource Name"
    )
    resource_unit_sb = models.CharField(
        max_length=20,
        verbose_name="Resource Unit",
        help_text="Unit of the resource (auto or manual entry)"
    )
    supplier_name_sb = models.ForeignKey(
        'po.PO',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sb_supplier_name_sb',
        verbose_name="Supplier Name"
    )
    po_quantity_sb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantity based on PO",
        help_text="Quantity of the resource"
    )
    unit_price_sb = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Unit Price"
    )
    receive_date_sb = models.DateField(
        verbose_name="Receive Date",
        help_text="Date of Receive"
    )
    actual_receive_quantity_sb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Actual Receive Quantity",
        help_text="Quantity of the resource"
    )
    bill_amount_sb = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto-calculated as-actual_receive_quantity_sb × unit_price_sb"
    )
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this SB"
    )
    manager_construction = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sbs",
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
        related_name="sbs_created",
        verbose_name="Created By"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sbs_updated",
        verbose_name="Updated By"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    def save(self, *args, **kwargs):            
        # Auto-calculate-bill_amount_sb #
        if self.actual_receive_quantity_sb and self.unit_price_sb:
            self.bill_amount_sb = self.actual_receive_quantity_sb * self.unit_price_sb
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_number_sb} - {self.project_name_sb}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "SB"
        verbose_name_plural = "SBs"