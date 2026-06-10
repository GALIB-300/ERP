# A - Import Required Modules #
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

# B - Role List for Price Event App #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# C - Profile Model to Assign Roles #
class PriceEventProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='price_event_profile'   # ✅ unique related_name
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in price event operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Price Event Role Profile"
        verbose_name_plural = "Price Event Role Profiles"

# D - Resource Price Change Event Model #
class ResourcePriceEvent(models.Model):
    # Core fields
    resource_name = models.CharField(max_length=100)
    supplier_name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    increase_decrease_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    # Effective date range
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    # Team role assignment
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this resource"
    )

    # Link resource to the user (Manager Construction)
    manager_construction = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="price_event_resources",   # ✅ unique related_name
        verbose_name="Manager Construction",
        null=True,
        blank=True
    )

    # Audit fields
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_price_events"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="updated_price_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # E - Save Logic #
    def save(self, *args, **kwargs):
        # Find last record for same resource/supplier
        last_record = ResourcePriceEvent.objects.filter(
            resource_name=self.resource_name,
            supplier_name=self.supplier_name
        ).order_by('-effective_from').first()

        if last_record and last_record != self:
            # Cumulative calculation based on last actual price
            self.actual_price = last_record.actual_price + self.increase_decrease_price
            # Close previous record validity
            last_record.effective_to = self.effective_from - timedelta(days=1)
            last_record.save(update_fields=['effective_to'])
        else:
            # First record → base + adjustment
            self.actual_price = self.base_price + self.increase_decrease_price

        super().save(*args, **kwargs)

    # F - String Representation #
    def __str__(self):
        return f"{self.resource_name} ({self.supplier_name}) - {self.actual_price}"

    # G - Meta Information #
    class Meta:
        ordering = ['-effective_from']
        verbose_name = "Resource Price Event"
        verbose_name_plural = "Resource Price Events"
