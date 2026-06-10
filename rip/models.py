# A - Import Required Modules #
from django.db import models
from django.contrib.auth.models import User   # Built-in User model
from datetime import timedelta

# B - Role list for RIP app #
ROLE_CHOICES = [
    ('manager_procurement', 'Manager Procurement'),
]

# C - Profile model to assign roles to users #
class RipProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='rip_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_procurement',
        help_text="Defines the user's role in RIP operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "RIP Role Profile"
        verbose_name_plural = "RIP Role Profiles"

# D - Resource Increase Price Model #
class Rip(models.Model):
    project_resource_supplier_name_rip = models.ForeignKey(
        'rbp.Rbp',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rip_project_name_rip',
        verbose_name="Project Name (RBP)"
    )
    project_name_rip = models.CharField(
        max_length=50,
        verbose_name="Unit",
        help_text="Unit of measure (auto from Resource)"
    )
    resource_name_rip = models.CharField(
        max_length=50,
        verbose_name="Unit",
        help_text="Unit of measure (auto from Resource)"
    )
    resource_unit_rip = models.CharField(
        max_length=50,
        verbose_name="Unit",
        help_text="Unit of measure (auto from Resource)"
    )
    supplier_name_rip = models.CharField(
        max_length=50,
        verbose_name="Unit",
        help_text="Unit of measure (auto from Resource)"
    )
    
    base_price_rip = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Base Price"
    )

    increase_decrease_price_rip = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Increase/Decrease Amount"
    )

    actual_base_price_rip = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Auto-calculated cumulatively"
    )

    effective_from = models.DateField(verbose_name="Price Change Date")
    effective_to = models.DateField(null=True, blank=True)

    team = models.CharField(
        max_length=50,
        default="manager_procurement",
        verbose_name="Team",
        help_text="Role/team associated with this RIP record"
    )

    # Link RIP to Manager Procurement #
    manager_procurement = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rips",
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
        related_name="rips_created",
        verbose_name="Created By"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rips_updated",
        verbose_name="Updated By"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    # E - Save Logic #
    def save(self, *args, **kwargs):
        # Project wise-Last record-shows-Ongoing #
        last_record = Rip.objects.filter(
            project_name_rip=self.project_name_rip,
            resource_name_rip=self.resource_name_rip,
            supplier_name_rip=self.supplier_name_rip
        ).order_by('-effective_from').first()

        if last_record and last_record != self:
            # Cumulative calculation based on last actual price #
            self.actual_base_price_rip = last_record.actual_base_price_rip + self.increase_decrease_price_rip
            # Close previous record validity #
            last_record.effective_to = self.effective_from - timedelta(days=1)
            last_record.save(update_fields=['effective_to'])
        else:
            # First record → base + adjustment
            inc_dec = self.increase_decrease_price_rip if self.increase_decrease_price_rip is not None else 0
            if self.base_price_rip is not None:
                self.actual_base_price_rip = self.base_price_rip + inc_dec

        super().save(*args, **kwargs)

    # F - String Representation #
    def __str__(self):
        return f"{self.resource_name_rip} ({self.supplier_name_rip})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Resource Price"
        verbose_name_plural = "Resource Prices"