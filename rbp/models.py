from django.db import models
from django.contrib.auth.models import User   # Built-in User model
from project.models import Project
from resource.models import Resource
from supplier.models import Supplier

# Role list for RBP app #
ROLE_CHOICES = [
    ('manager_procurement', 'Manager Procurement'),
]

# Profile model to assign roles to users #
class RbpProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='rbp_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_procurement',
        help_text="Defines the user's role in RBP operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "RBP Role Profile"
        verbose_name_plural = "RBP Role Profiles"

# Resource Base Price Model #
class Rbp(models.Model):
    project_name_rbp = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rbp_project_name_rbp',
        verbose_name="Project Name"
    )

    resource_name_rbp = models.ForeignKey(
        'resource.Resource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rbp_resource_name_rbp',
        verbose_name="Resource Name"
    )

    resource_unit_rbp = models.CharField(
        max_length=50,
        verbose_name="Unit",
        help_text="Unit of measure (auto from Resource)"
    )

    supplier_name_rbp = models.ForeignKey(
        'supplier.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rbp_supplier_name_rbp',
        verbose_name="Supplier Name"
    )
    
    price_select_date = models.DateField(
        verbose_name="Price Change Date"
    )

    resource_base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Base Price"
    )

    resource_discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Discount Price"
    )

    actual_base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Actual Base Price"
    )

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_procurement',
        help_text="Team responsible for this rp"
    )

    # Link RBP to Manager Procurement #
    manager_procurement = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rbps",
        verbose_name="Manager Procurement",
        null=True,
        blank=True
    )

    # ERP compulsory audit fields #
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rbps_created",
        verbose_name="Created By",
        help_text="User who created this RBP record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rbps_updated",
        verbose_name="Updated By",
        help_text="User who last updated this RBP record"
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
        # Auto-calculate Actual Base Price #
        if self.resource_base_price is not None and self.resource_discount_price is not None:
            self.actual_base_price = self.resource_base_price - self.resource_discount_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_name_rbp} | {self.resource_name_rbp} | {self.supplier_name_rbp}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Resource Price"
        verbose_name_plural = "Resource Prices"
