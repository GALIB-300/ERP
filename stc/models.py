from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for stc app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users #
class StcProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='stc_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in stc operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "STC Role Profile"
        verbose_name_plural = "STC Role Profiles"

# STC Model #
class Stc(models.Model):
    project_name_stc = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stc_project_name_stc',
        verbose_name="Project Name"
    )
    supplier_name_stc = models.ForeignKey(
        'supplier.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stc_supplier_name_stc',
        verbose_name="Supplier Name"
    )
    po_date_stc = models.DateField(
        verbose_name="PO Date",
        help_text="Date of STC PO"
    )
    po_no_stc = models.CharField(
        max_length=20,
        verbose_name="PO No",
        help_text="Number of STC PO"
    )
    vat_ait_stc = models.CharField(
        max_length=10,
        choices=[('Include', 'Include'), ('Exclude', 'Exclude')],
        default='Include',
        verbose_name="VAT/AIT",
        help_text="VAT/AIT inclusion status"
    )
    delivery_term_stc = models.TextField(
        verbose_name="Delivery Term",
        help_text="Terms of delivery"
    )
    payment_term_stc = models.TextField(
        verbose_name="Payment Term",
        help_text="Terms of payment"
    )
    warranty_term_stc = models.TextField(
        verbose_name="Warranty Term",
        help_text="Terms of warranty"
    )

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this STC PO"
    )

    manager_construction = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stcs",
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
        related_name="stcs_created",
        verbose_name="Created By"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stcs_updated",
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
        if self.po_date_stc and self.po_no_stc:
            # Extract year from po_date_stc
            year_str = self.po_date_stc.strftime("%Y")

            # Take the raw PO number you typed (e.g. "1", "2")
            raw_number = str(self.po_no_stc).replace(f"PO-{year_str}-", "")

            # Format as STC-YYYY-<number>
            self.po_no_stc = f"PO-{year_str}-{raw_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_no_stc} - {self.project_name_stc}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "STC"
        verbose_name_plural = "STCs"
