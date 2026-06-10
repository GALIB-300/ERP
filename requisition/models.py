from django.db import models
from django.contrib.auth.models import User   # Built-in User model

from project.models import Project
from resource.models import Resource

# Role list for requisition app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users #
class RequisitionProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='requisition_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in requisition operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Requisition Role Profile"
        verbose_name_plural = "Requisition Role Profiles"

# Requisition Model #
class Requisition(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    project_name_requisition = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisition_project_name_requisition',
        verbose_name="Project Name"
    )
    requisition_date = models.DateField()
    requisition_no = models.CharField(max_length=50)
    resource_name_requisition = models.ForeignKey(
        Resource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisition_resource_name_requisition',
        verbose_name="Resource Name"
    )
    resource_unit_requisition = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_date = models.DateField()
    remarks = models.CharField(max_length=50, default="NA")   # 👈 Default NA
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # 👈 Dropdown status
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        help_text="Team responsible for this requisition"
    )
    allow_team_edit = models.BooleanField(
        default=False,
        help_text="If True, allows the team member who created this record to edit/delete it"
    )
    edit_request_pending = models.BooleanField(
        default=False,
        help_text="If True, indicates the team member has requested edit/delete access"
    )
    submitted_for_approval = models.BooleanField(
        default=False,
        help_text="Checked when user sends this requisition to admin for approval"
    )
    # Link requisition to the user (Manager Construction) #
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="requisitions",
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
        related_name="requisitions_created",
        verbose_name="Created By",
        help_text="User who created this requisition record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisitions_updated",
        verbose_name="Updated By",
        help_text="User who last updated this requisition record"
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
        return f"{self.resource_name_requisition} - {self.requisition_no}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Requisition"
        verbose_name_plural = "Requisitions"
