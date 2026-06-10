from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for resource app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
    ('manager_sales', 'Manager Sales'),   # ✅ Added for Belal
]

# Profile model to assign roles to users #
class ResourceProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='resource_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',   # Default remains construction
        help_text="Defines the user's role in resource operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Resource Role Profile"
        verbose_name_plural = "Resource Role Profiles"

# Main model for storing resource details #
UNIT_CHOICES = [
    ('bag', 'Bag'),
    ('pcs', 'Pcs'),
    ('nos', 'Nos'),
    ('kg', 'Kg'),
    ('ltr', 'Ltr'),
    ('sft', 'Sft'),
    ('cft', 'Cft'),
    ('bundle', 'Bundle'),
    ('ton', 'Ton'),
]

RESOURCE_GROUP_CHOICES = [
    ('civil_work_resource', 'Civil Work Resource'),
    ('sanitary_work_resource', 'Sanitary Work Resource'),
    ('electrical_work_resource', 'Electrical Work Resource'),
]

class Resource(models.Model):
    name_of_resource = models.CharField(
        max_length=100,
        help_text="Name of the resource",
        unique=True,
        verbose_name="Resource Name"
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        verbose_name="Unit",
        help_text="Select the measurement unit"
    )
    resource_group = models.CharField(
        max_length=30,  # Increased to fit longest choice value
        choices=RESOURCE_GROUP_CHOICES,
        verbose_name="Resource Group",
        help_text="Select the resource group"
    )
    team = models.CharField(   
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this resource"
    )
    # Link resource to the user (Manager Construction) #
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="resources",
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
        related_name="resources_created",
        verbose_name="Created By",
        help_text="User who created this resource record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources_updated",
        verbose_name="Updated By",
        help_text="User who last updated this resource record"
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
        return self.name_of_resource

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

