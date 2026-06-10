from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    DEPARTMENT_CHOICES = [
        ('construction', 'Construction'),
        ('salesmarketing', 'Sales & Marketing'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Use ManyToManyField instead of CharField
    departments = models.ManyToManyField(
        'Department',
        blank=True
    )

    def __str__(self):
        dept_names = ", ".join([d.name for d in self.departments.all()])
        return f"{self.user.username} - {dept_names}"

class Department(models.Model):
    name = models.CharField(
        max_length=50,
        choices=Profile.DEPARTMENT_CHOICES,
        unique=True
    )

    def __str__(self):
        return self.get_name_display() if hasattr(self, "get_name_display") else self.name
