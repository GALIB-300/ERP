from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for po app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users #
class PoProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='po_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in po operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "PO Role Profile"
        verbose_name_plural = "PO Role Profiles"

# PO Model #
class Po(models.Model):
    project_name_po = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='po_project_name_po',
        verbose_name="Project Name"
    )
    po_date = models.DateField(
        verbose_name="PO Date",
        help_text="Date of PO"
    )
    po_no = models.CharField(
        max_length=20,
        verbose_name="PO No",
        help_text="No of PO"
    )
    resource_name_po = models.ForeignKey(
        'resource.Resource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='po_resource_name_po',
        verbose_name="Resource Name"
    )
    resource_unit_po = models.CharField(
        max_length=20,
        verbose_name="Resource Unit",
        help_text="Unit of the resource (auto or manual entry)"
    )
    supplier_name_po = models.ForeignKey(
        'supplier.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='po_supplier_name_po',
        verbose_name="Supplier Name"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantity",
        help_text="Quantity of the resource"
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Unit Price"
    )
    bill_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto-calculated as Quantity × Unit Price"
    )
    delivery_date = models.DateField(
        verbose_name="Delivery Date",
        help_text="Date of Delivery"
    )

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this PO"
    )

    manager_construction = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pos",
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
        related_name="pos_created",
        verbose_name="Created By"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pos_updated",
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
        if self.po_date and self.po_no:
            # Extract year from po_date
            year_str = self.po_date.strftime("%Y")

            # Take the raw PO number you typed (e.g. "1", "2")
            raw_number = str(self.po_no).replace(f"PO-{year_str}-", "")

            # Format as PO-YYYY-<number>
            self.po_no = f"PO-{year_str}-{raw_number}"
            
        # Auto-calculate-bill_amount #
        if self.quantity and self.unit_price:
            self.bill_amount = self.quantity * self.unit_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_no} - {self.project_name_po}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "PO"
        verbose_name_plural = "POs"
