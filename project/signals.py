# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProjectProfile

# B - Signal: Create ProjectProfile When User Is Created #
@receiver(post_save, sender=User)
def create_project_profile(sender, instance, created, **kwargs):
    if created:
        ProjectProfile.objects.create(user=instance)
