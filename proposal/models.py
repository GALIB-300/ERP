from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for proposal app #
ROLE_CHOICES = [
    ('manager_sales', 'Manager Sales'),
]

# Profile model to assign roles to users #
class ProposalProfile(models.Model):
    user = models.OneToOneField(
        User,   
        on_delete=models.CASCADE,
        related_name='proposal_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Defines the user's role in proposal operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Proposal Role Profile"
        verbose_name_plural = "Proposal Role Profiles"

# Main model for storing proposal details #
class Proposal(models.Model):
    SUBMIT_CHOICES = [
        ('Physically', 'Physically'),
        ('By Email', 'By Email'),
    ]
    proposal_prepare_date = models.DateField(
        verbose_name="Proposal Date",
        help_text="Date of Proposal"
    )
    proposal_no = models.CharField(
        max_length=20,
        verbose_name="Proposal No",
        help_text="No of Proposal"
    )
    customer_name_proposal = models.CharField(
    max_length=100,
    verbose_name="Customer Name",
    help_text="Enter the customer name"
)
    description_of_proposal = models.TextField(
        verbose_name="Description of Proposal",
        help_text="Proposal Description"
    )
    proposal_submit_date = models.DateField(
        verbose_name="Proposal Date",
        help_text="Date of Proposal"
    )
    submit_year = models.PositiveIntegerField(
        editable=False,
        null=True,
        blank=True,
        verbose_name="Submit Year",
        help_text="Auto-filled year from submit date"
    )
    submit_by = models.CharField(
        max_length=10,
        choices=SUBMIT_CHOICES,
        verbose_name="Submit",
        help_text="Select the submit process"
    )
    proposal_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=True,
        default=0,
        help_text="Proposal amount"
    )
    team = models.CharField(   
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Team responsible for the proposal"
    )
    # Link supplier to the user (Manager Sales) #
    manager_sales = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="proposals",
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
        related_name="proposals_created",
        verbose_name="Created By",
        help_text="User who created this proposal record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proposals_updated",
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
        # Auto-fill submit_year from proposal_submit_date
        if self.proposal_submit_date:
            self.submit_year = self.proposal_submit_date.year
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.customer_name_proposal)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Proposal"
        verbose_name_plural = "Proposals"
