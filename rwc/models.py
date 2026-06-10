from django.db import models
from django.contrib.auth.models import User   # Built-in User model
from company.models import Company
from project.models import Project   # ✅ Import Project model

# Role list for rwc app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users #
class RwcProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='rwc_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in rwc operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Rwc Role Profile"
        verbose_name_plural = "Rwc Role Profiles"


# Main model for storing rwc details #
class Rwc(models.Model):
    requisition_date = models.DateField()
    requisition_no = models.CharField(max_length=50, blank=True)   # ⚠️ removed unique=True
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    project_name_rwc = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rwc_project_name_rwc',
        verbose_name="Project Name"
    )
    delivery_date = models.DateField()

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this rwc"
    )

    # Link resource to the user (Manager Construction) #
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="rwcs",
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
        related_name="rwcs_created",
        verbose_name="Created By",
        help_text="User who created this rwc record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rwcs_updated",
        verbose_name="Updated By",
        help_text="User who last updated this rwc record"
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

    # Snapshot fields #
    company_name = models.CharField(max_length=200, blank=True)
    company_address = models.CharField(max_length=250, blank=True)
    company_email = models.EmailField(blank=True)
    company_contact_no = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Rwc"
        verbose_name_plural = "Rwcs"

    def save(self, *args, **kwargs):
        # Step-(A)-Copy company info into snapshot fields #
        if self.company:
            self.company_name = self.company.company_name
            self.company_address = self.company.company_address
            self.company_email = self.company.company_email
            self.company_contact_no = self.company.company_contact_no

        # Step-(B)-Generate requisition_no only on create #
        if not self.pk and self.requisition_date and self.project_name_rwc:
            year_str = self.requisition_date.strftime("%Y")

            # ✅ Count existing requisitions per project + year
            count = Rwc.objects.filter(
                requisition_date__year=self.requisition_date.year,
                company=self.company,
                project_name_rwc=self.project_name_rwc
            ).count() + 1

            # ✅ Requisition number resets per project
            self.requisition_no = f"RQ-{year_str}-{count}"

        # Step-(C)-Save record #
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.requisition_no} - {self.company_name}"
