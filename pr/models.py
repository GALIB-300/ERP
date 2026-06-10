# A - Import Required Modules #
from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# B - Role list for PR app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# C - Profile model to assign roles to users #
class PrProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='pr_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in PR operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "PR Role Profile"
        verbose_name_plural = "PR Role Profiles"

# D - Main model for storing PR details #
class Pr(models.Model):
    project_name_pr = models.ForeignKey(
        'project.Project',   # ✅ Cross-app reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prs",
        verbose_name="Project Name"
    )

    requisition_date_pr = models.DateField(
        verbose_name="Requisition Date",
        help_text="Date of Requisition"
    )

    requisition_no_pr = models.CharField(
        max_length=20,
        verbose_name="Requisition No",
        help_text="No of Requisition"
    )

    resource_name_pr = models.ForeignKey(
        'resource.Resource',   # ✅ Cross-app reference
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="prs",
        verbose_name="Resource Name",
        help_text="Select the resource"
    )

    resource_unit_pr = models.CharField(
        max_length=20,
        verbose_name="Resource Unit",
        help_text="Unit of the resource (auto or manual entry)"
    )

    quantity_pr = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantity",
        help_text="Quantity of the resource"
    )

    delivery_date_pr = models.DateField(
        verbose_name="Delivery Date",
        help_text="Date of Delivery"
    )

    remarks_pr = models.TextField(
        verbose_name="Remarks",
        help_text="Additional notes or comments for this PR",
        blank=True,
        null=True,
        default="NA"
    )
    
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this PR"
    )

    manager_construction = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="prs",
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
        related_name="prs_created",
        verbose_name="Created By"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prs_updated",
        verbose_name="Updated By"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    def save(self, *args, **kwargs):
        # ✅ Generate requisition_no only on create
        if not self.pk and self.requisition_date_pr and self.project_name_pr:
            year_str = self.requisition_date_pr.strftime("%Y")

            # ✅ Look for existing requisition with same project + same date
            existing = Pr.objects.filter(
                project_name_pr=self.project_name_pr,
                requisition_date_pr=self.requisition_date_pr
            ).first()

            if existing:
                # ✅ Reuse the same requisition_no for all resources
                self.requisition_no_pr = existing.requisition_no_pr
            else:
                # ✅ First requisition for this project/date → start at 1
                self.requisition_no_pr = f"RQ-{year_str}-1"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.requisition_no_pr} - {self.project_name_pr}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "PR"
        verbose_name_plural = "PRs"