from django.db import models
from django.contrib.auth.models import User   # Built-in User model
from proposal.models import Proposal

# Role list for pfp app #
ROLE_CHOICES = [
    ('manager_sales', 'Manager Sales'),
]

# Profile model to assign roles to users #
class PfpProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='pfp_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Defines the user's role in pfp operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "PFP Role Profile"
        verbose_name_plural = "PFP Role Profiles"

# PFP Model #
class Pfp(models.Model):
    proposal = models.OneToOneField(
        Proposal,                 
        on_delete=models.CASCADE, 
        related_name="pfp_record",
        verbose_name="Linked Proposal"
    )
    title_pfp = models.TextField(
        verbose_name="Proposal Front Page",
        help_text="Front Page of Proposal"
    )
    submit_to_pfp = models.TextField(
        verbose_name="Proposal Submit To",
        help_text="Submit of Proposal To"
    )
    submit_by_pfp = models.TextField(
        verbose_name="Proposal Submit By",
        help_text="Submit of Proposal By"
    )

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Team responsible for this PFP"
    )

    manager_sales = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pfps",
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
        related_name="pfps_created",
        verbose_name="Created By"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pfps_updated",
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

    # Snapshot fields
    customer_name_proposal = models.CharField(max_length=255)
    proposal_prepare_date = models.DateField()
    proposal_no = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if self.proposal:
            self.customer_name_proposal = self.proposal.customer_name_proposal
            self.proposal_prepare_date = self.proposal.proposal_prepare_date
            self.proposal_no = self.proposal.proposal_no
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_name_proposal}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "PFP"
        verbose_name_plural = "PFPs"
