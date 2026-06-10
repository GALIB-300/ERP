from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for pt app #
ROLE_CHOICES = [
    ('manager_sales', 'Manager Sales'),
]

# Profile model to assign roles to users #
class PtProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='pt_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Defines the user's role in pt operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "PT Role Profile"
        verbose_name_plural = "PT Role Profiles"


# Main model for storing proposal details in pt app #
class Pt(models.Model):
    PROPOSAL_INFORMATION_CHOICES = [
        ('Sales Person-A', 'Sales Person-A'),
        ('Sales Person-B', 'Sales Person-B'),
        ('Sales Person-C', 'Sales Person-C'),
        ('Sales Person-D', 'Sales Person-D'),
    ]

    STATUS_PROPOSAL_CHOICES = [
        ('Award', 'Award'),
        ('Not Award', 'Not Award'),
        ('Pending', 'Pending'),
    ]

    client_name_pt = models.ForeignKey(
        'client.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pt_client_name_pt',
        verbose_name="Client Name"
    )
    proposal_information_collect_pt = models.CharField(
        max_length=20,
        choices=PROPOSAL_INFORMATION_CHOICES,
        verbose_name="Proposal Information Source",
        help_text="Source from which proposal information is collected"
    )
    description_work_pt = models.TextField(
        help_text="Detailed description of the work in the proposal",
        verbose_name="Work Description"
    )
    total_proposal_pt = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=1,
        help_text="Total proposal amount (fixed to 1)",
        verbose_name="Total Proposal"
    )
    prepare_date_pt = models.DateField(
        help_text="Date when the proposal was prepared",
        verbose_name="Prepare Date"
    )
    submit_date_pt = models.DateField(
        help_text="Date when the proposal was submitted",
        verbose_name="Submit Date"
    )
    submit_year_pt = models.PositiveIntegerField(
        help_text="Year of submission",
        verbose_name="Submit Year"
    )
    status_proposal_pt = models.CharField(
        max_length=20,
        choices=STATUS_PROPOSAL_CHOICES,
        verbose_name="Status Proposal",
        help_text="Proposal for Status"
    )
    proposal_award_pt = models.IntegerField(
    default=0,
    help_text="1 = Award, 0 = Not Award or Pending",
    verbose_name="Proposal Award"
)
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Team responsible for this proposal"
    )
    manager_sales = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pt_proposals",
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
        related_name="pt_created",
        verbose_name="Created By",
        help_text="User who created this proposal record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pt_updated",
        verbose_name="Updated By",
        help_text="User who last updated this proposal record"
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
        # Auto-fill submit_year_pt from submit_date_pt #
        if self.submit_date_pt:
            self.submit_year_pt = self.submit_date_pt.year

        # Auto-set proposal_award_pt based on status_proposal_pt
        if self.status_proposal_pt == "Award":
         self.proposal_award_pt = 1   # Award → show 1
        elif self.status_proposal_pt in ["Not Award", "Pending"]:
         self.proposal_award_pt = 0   # Not Award / Pending → show 0
        else:
         self.proposal_award_pt = 0   # Default safeguard

        # Force total_proposal_pt to always be 1 #
        self.total_proposal_pt = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_name_pt} - {self.status_proposal_pt}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "PT Proposal"
        verbose_name_plural = "PT Proposals"
