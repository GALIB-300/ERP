from django.db import models
from django.contrib.auth.models import User   

# Role list for letter app #
ROLE_CHOICES = [
    ('manager_sales', 'Manager Sales'),
]

# Profile model to assign roles to users #
class LetterProfile(models.Model):
    user = models.OneToOneField(
        User,   
        on_delete=models.CASCADE,
        related_name='letter_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Defines the user's role in letter operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Letter Role Profile"
        verbose_name_plural = "Letter Role Profiles"

# Main model for storing letter #
class Letter(models.Model):
    client_name_letter = models.ForeignKey(
        'cba.Cba',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='letter_client_name_letter',
        verbose_name="Client Name"
    )

    wo_no_letter = models.ForeignKey(
        'cba.Cba',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='letter_wo_no_letter',
        verbose_name="WO No"
    )

    bill_no_letter = models.ForeignKey(
        'cba.Cba',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='letter_bill_no_letter',
        verbose_name="Bill No"
    )

    # --- Letter Date --- #
    date = models.DateField(
        verbose_name="Letter Date",
        help_text="Date of the letter"
    )

    # --- Recipient Info --- #
    recipient_name = models.CharField(
        max_length=150,
        verbose_name="Recipient Name",
        help_text="Full name of the recipient"
    )

    recipient_designation = models.CharField(
        max_length=150,
        verbose_name="Recipient Designation",
        help_text="Designation of the recipient",
        blank=True,
        null=True
    )

    recipient_address = models.TextField(
        verbose_name="Recipient Address",
        help_text="Address of the recipient",
        blank=True,
        null=True
    )

    # --- Letter Subject --- #
    subject = models.CharField(
        max_length=255,
        verbose_name="Subject",
        help_text="Subject line of the letter",
        default="Subject: Request for Bill – Supply of Design & Drawing"
    )

    # --- Recipient Salutation --- #
    recipient_salutation = models.CharField(
        max_length=50,
        verbose_name="Salutation",
        help_text="Salutation used in the letter",
        default="Dear Sir"
    )

    # --- Letter Body --- #
    body = models.TextField(
        verbose_name="Letter Body",
        help_text="Main content of the letter",
        default=(
            "We acknowledge receipt of the design and drawing materials supplied by your office "
            "in connection with our project requirements. To complete our records and proceed with "
            "payment formalities, we kindly request you to issue the corresponding bill/invoice for "
            "the supplied design and drawing.\n\n"
            "Please ensure the bill includes:\n\n"
            "Reference to the project name and requisition/order number\n\n"
            "Date of supply\n\n"
            "Detailed description of the design and drawing provided\n\n"
            "Applicable charges and payment terms\n\n"
            "We would appreciate receiving the bill at your earliest convenience so that we may "
            "process it without delay.\n\n"
            "Thank you for your cooperation.\n\n"
            "Sincerely,"
        )
    )

    # --- Sender Info --- #
    sender_name = models.CharField(
        max_length=150,
        verbose_name="Sender Name",
        help_text="Full name of the sender"
    )

    sender_designation = models.CharField(
        max_length=150,
        verbose_name="Sender Designation",
        help_text="Designation of the sender",
        blank=True,
        null=True
    )

    sender_company_name = models.CharField(
        max_length=150,
        verbose_name="Sender Company Name",
        help_text="Company name of the sender",
        blank=True,
        null=True
    )

    remarks = models.TextField(
        max_length=255,
        verbose_name="Remarks",
        help_text="Remarks",
        default="NA"
    )

    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_sales',
        help_text="Team responsible for this letter"
    )

    manager_sales = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="letter",
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
        related_name="letter_created",
        verbose_name="Created By",
        help_text="User who created this letter record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="letter_updated",
        verbose_name="Updated By",
        help_text="User who last updated this letter record"
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
        return f"{self.recipient_name} - {self.recipient_designation}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Letter"
        verbose_name_plural = "Letter"
