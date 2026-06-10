from django.db import models
from django.contrib.auth.models import User   # Built-in User model
from django.utils import timezone             # Needed for planned_progress

# Role list for ws app #
ROLE_CHOICES = [
    ('manager_construction', 'Manager Construction'),
]

# Profile model to assign roles to users #
class WsProfile(models.Model):
    user = models.OneToOneField(
        User,   # Using built-in User
        on_delete=models.CASCADE,
        related_name='ws_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Defines the user's role in ws operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "WS Role Profile"
        verbose_name_plural = "WS Role Profiles"

# WS Model #
class Ws(models.Model):
    project_name_ws = models.CharField(
        max_length=100,
        help_text="Name of the project",
        verbose_name="Project Name"
    )

    task_name_ws = models.CharField(
        max_length=100,
        help_text="Name of the task",
        verbose_name="Task Name"
    )

    planned_start = models.DateField()
    planned_finish = models.DateField()
    start_date = models.DateField()
    finish_date = models.DateField()
    actual_progress = models.PositiveIntegerField(default=0, verbose_name="Actual Progress")
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager_construction',
        help_text="Team responsible for this ws"
    )
    # Link wp to the user (Manager Construction) #
    manager_construction = models.ForeignKey(
        User,   # Built-in User
        on_delete=models.CASCADE,
        related_name="wss",
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
        related_name="wss_created",
        verbose_name="Created By",
        help_text="User who created this ws record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wss_updated",
        verbose_name="Updated By",
        help_text="User who last updated this ws record"
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

    class Meta:
        ordering = ['created_at']
        verbose_name = "WS"
        verbose_name_plural = "WSs"

    # Calculation #
    @property
    def planned_duration(self):
        return (self.planned_finish - self.planned_start).days

    @property
    def actual_duration(self):
        return (self.finish_date - self.start_date).days

    @property
    def duration_variance(self):
        return self.actual_duration - self.planned_duration

    @property
    def planned_progress(self):
        today = timezone.now().date()
        if today < self.planned_start:
            return 0
        if today > self.planned_finish:
            return 100
        elapsed = (today - self.planned_start).days
        return round((elapsed / self.planned_duration) * 100, 2)

    def __str__(self):
        return f"{self.project_name_ws} | {self.task_name_ws}"



