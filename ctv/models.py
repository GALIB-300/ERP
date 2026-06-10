# A - Import Required Modules #
from django.db import models
from django.contrib.auth.models import User   # Built-in User model
from decimal import Decimal

# B - Role list for ctv app #
ROLE_CHOICES = [
    ('manager_sales', 'Manager Sales'),
]

# C - Profile model to assign roles to users #
class CtvProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ctv_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Defines the user's role in CTV operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "CTV Role Profile"
        verbose_name_plural = "CTV Role Profiles"

# D - Main model for storing CTV details #
class Ctv(models.Model):
    VAT_AIT_CTV_CHOICES = [
        ('Include', 'Include'),
        ('Exclude', 'Exclude'),
    ]
    VAT_CTV_CHOICES = [
        ('6.5%', '6.5%'),
        ('0%', '0%'),
    ]
    AIT_CTV_CHOICES = [
        ('13%', '13%'),
        ('0%', '0%'),
    ]

    client_name_ctv = models.ForeignKey(
        'pt.Pt',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ctv_client_name_ctv',
        verbose_name="Client Name"
    )
    project_id_ctv = models.CharField(
        max_length=100,
        help_text="Project ID",
        verbose_name="Project ID"
    )
    wo_no_ctv = models.CharField(
        max_length=100,
        help_text="Work Order Number",
        verbose_name="WO No"
    )
    description_work_ctv = models.TextField(
        help_text="Description of Work",
        verbose_name="Work Description"
    )
    start_date_ctv = models.DateField(
        help_text="Start Date of the project",
        verbose_name="Start Date"
    )
    finish_date_ctv = models.DateField(
        help_text="Finish Date of the project",
        verbose_name="Finish Date"
    )
    contract_value_ctv = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Contract Value",
        verbose_name="Contract Value"
    )
    vat_ait_ctv = models.CharField(
        max_length=10,
        choices=VAT_AIT_CTV_CHOICES,
        verbose_name="VAT + AIT",
        help_text="VAT + AIT combined"
    )
    vat_ctv = models.CharField(
        max_length=10,
        choices=VAT_CTV_CHOICES,
        verbose_name="VAT",
        help_text="VAT"
    )
    ait_ctv = models.CharField(
        max_length=10,
        choices=AIT_CTV_CHOICES,
        verbose_name="AIT",
        help_text="AIT"
    )
    vat_ait_amount_ctv = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="VAT & AIT Amount",
    )
    actual_contract_value_ctv = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Actual Contract Value after VAT/AIT",
    )

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Team responsible for this contract"
    )
    manager_sales = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ctv_contracts",
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
        related_name="ctv_created",
        verbose_name="Created By",
        help_text="User who created this contract record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ctv_updated",
        verbose_name="Updated By",
        help_text="User who last updated this contract record"
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

    def save(self, *args, **kwargs):
        # Convert VAT and AIT to Decimal, stripping %
        vat_rate = Decimal(self.vat_ctv.replace("%", "")) if self.vat_ctv else Decimal("0.0")
        ait_rate = Decimal(self.ait_ctv.replace("%", "")) if self.ait_ctv else Decimal("0.0")

        # ✅ VAT + AIT amount
        self.vat_ait_amount_ctv = (
            (self.contract_value_ctv * vat_rate) + (self.contract_value_ctv * ait_rate)
        ) / Decimal("100")

        # ✅ Actual Contract Value
        self.actual_contract_value_ctv = self.contract_value_ctv - self.vat_ait_amount_ctv

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_name_ctv} - {self.project_id_ctv}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contract Value (CTV)"
        verbose_name_plural = "Contract Values (CTV)"