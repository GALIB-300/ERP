from django.db import models
from django.contrib.auth.models import User   # Built-in User model

# Role list for project app
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users
class ProjectProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='project_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in project operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Project Role Profile"
        verbose_name_plural = "Project Role Profiles"

# Main model for storing project details
class Project(models.Model):
    name_of_project = models.CharField(
        max_length=100,
        help_text="Name of the project",
        unique=True,
        verbose_name="Project Name"
    )
    project_address = models.CharField(
        max_length=200,
        help_text="Project site address",
        verbose_name="Project Address"
    )
    contact_person_name = models.CharField(
        max_length=100,
        help_text="Primary contact person for the project",
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
        help_text="Team responsible for this project"
    )
    # Link project to the user (Manager Construction)
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="projects",
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
        related_name="projects_created",
        verbose_name="Created By",
        help_text="User who created this project record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_updated",
        verbose_name="Updated By",
        help_text="User who last updated this project record"
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
        return self.name_of_project

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"


