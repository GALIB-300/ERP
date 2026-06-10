from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for supplier app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
    ('gm_construction', 'GM Construction'),
    
]

# Profile model to assign roles to users #
class SupplierProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='supplier_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in supplier operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Supplier Role Profile"
        verbose_name_plural = "Supplier Role Profiles"

# Main model for storing supplier details #
class Supplier(models.Model):
    name_of_supplier = models.CharField(
        max_length=100,
        help_text="Name of the supplier",
        unique=True,
        verbose_name="Supplier Name"
    )
    supplier_contact_person = models.CharField(
        max_length=100,
        verbose_name="Supplier Contact Person",
        help_text="Enter the supplier contact person's name"
    )
    supplier_address = models.CharField(
        max_length=200,
        verbose_name="Supplier Address",
        help_text="Enter the supplier's address"
    )
    supplier_contact_number = models.CharField(
        max_length=20,
        help_text="Phone number of the supplier",
        verbose_name="Supplier Contact Number"
    )
    team = models.CharField(   
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for the supplier"
    )
    # Link supplier to the user (Manager Construction) #
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="suppliers",
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
        related_name="suppliers_created",
        verbose_name="Created By",
        help_text="User who created this supplier record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suppliers_updated",
        verbose_name="Updated By",
        help_text="User who last updated this suppler record"
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

    def __str__(self):
        return self.name_of_supplier

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
