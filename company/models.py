from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for company app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users #
class CompanyProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='company_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in company operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Company Role Profile"
        verbose_name_plural = "Company Role Profiles"

# Main model for storing company details #
class Company(models.Model):
    company_name = models.CharField(
        max_length=100,
        help_text="Name of the company",
        unique=True,
        verbose_name="Company Name"
    )
    company_address = models.CharField(
    max_length=255,   # allows full street address
    verbose_name="Company Address",
    help_text="Enter the company address"
)
    company_email = models.EmailField(
        max_length=254,   # Django default max length for emails
        verbose_name="Company Email",
        help_text="Enter the official company email address"
    )
    company_contact_no = models.CharField(
        max_length=20,
        verbose_name="Company Contact Number",
        help_text="Enter the company phone/mobile number"
    )

    team = models.CharField(   
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this company"
    )
    # Link company to the user (Manager Construction) #
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="companies",
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
        related_name="companies_created",
        verbose_name="Created By",
        help_text="User who created this company record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies_updated",
        verbose_name="Updated By",
        help_text="User who last updated this company record"
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
        return self.company_name

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Company"
        verbose_name_plural = "Companies"
