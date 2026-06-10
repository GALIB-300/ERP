from django.db import models
from django.contrib.auth.models import User   

# Role list for client app #
ROLE_CHOICES = [
    ('manager_sales', 'Manager Sales'),
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users
class ClientProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='client_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Defines the user's role in client operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Client Role Profile"
        verbose_name_plural = "Client Role Profiles"

# Main model for storing client details
class Client(models.Model):
    name_of_client = models.CharField(
        max_length=100,
        help_text="Name of the client",
        unique=True,
        verbose_name="Client Name"
    )
    client_address = models.CharField(
        max_length=200,
        help_text="Client site address",
        verbose_name="Client Address"
    )
    contact_person_name = models.CharField(
        max_length=100,
        help_text="Primary contact person for the client",
        verbose_name="Contact Person Name"
    )
    contact_person_number = models.CharField(
        max_length=20,
        help_text="Phone number of the contact person",
        verbose_name="Contact Person Number"
    )
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this client"
    )
    # Link client to the user (Manager Construction)
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name="Manager Construction",
        null=True,
        blank=True
    )
    # ERP compulsory audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients_created",
        verbose_name="Created By",
        help_text="User who created this client record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients_updated",
        verbose_name="Updated By",
        help_text="User who last updated this client record"
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
        return self.name_of_client

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Client"
        verbose_name_plural = "Clients"
