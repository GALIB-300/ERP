from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for cba app #
ROLE_CHOICES = [
    ('manager_sales', 'Manager Sales'),
]

# Profile model to assign roles to users #
class CbaProfile(models.Model):
    user = models.OneToOneField(
        User,   
        on_delete=models.CASCADE,
        related_name='cba_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Defines the user's role in cba operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "CBA Role Profile"
        verbose_name_plural = "CBA Role Profiles"

# Main model for storing contract value details #
class Cba(models.Model):
    VAT_AIT_CBA_CHOICES = [
        ('Include', 'Include'),
        ('Exclude', 'Exclude'),
    ]

    client_name_cba = models.ForeignKey(
        'ctv.Ctv',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cba_client_name_cba',
        verbose_name="Client Name"
    )
    project_id_cba = models.ForeignKey(
        'ctv.Ctv',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cba_project_id_cba',
        verbose_name="Project ID"
    )
    wo_no_cba = models.ForeignKey(
        'ctv.Ctv',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cba_wo_no_cba',
        verbose_name="WO Number"
    )
    bill_date_cba = models.DateField(
        help_text="Bill Date",
        verbose_name="Bill Date"
    )
    bill_no_cba = models.CharField(
        max_length=100,
        help_text="Bill Number",
        verbose_name="Bill No"
    )
    vat_ait_cba = models.CharField(
        max_length=10,
        choices=VAT_AIT_CBA_CHOICES,
        verbose_name="VAT + AIT",
        help_text="VAT + AIT combined"
    )
    bill_amount_cba = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Bill Amount",
        verbose_name="Bill Amount"
    )
    vat_ait_amount_cba = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="VAT & AIT Amount",
        verbose_name="VAT & AIT Amount"
    )
    actual_bill_amount_cba = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto-calculated field"
    )

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Team responsible for this cba"
    )
    manager_sales = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cba_contracts",
        verbose_name="Manager Sales",
        null=True,
        blank=True
    )

    # ERP compulsory audit fields #
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cba_created",
        verbose_name="Created By",
        help_text="User who created this cba record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cba_updated",
        verbose_name="Updated By",
        help_text="User who last updated this cba record"
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

    # Simple formula: Actual Bill Amount = Bill Amount − VAT & AIT Amount #
    def save(self, *args, **kwargs):
        vat_ait = self.vat_ait_amount_cba if self.vat_ait_amount_cba is not None else 0
        if self.bill_amount_cba is not None:
            self.actual_bill_amount_cba = self.bill_amount_cba - vat_ait
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_name_cba} - {self.project_id_cba}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "CBA"
        verbose_name_plural = "CBA"
