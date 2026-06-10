# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PtProfile

# B - Signal: Create PtProfile When User Is Created #
@receiver(post_save, sender=User)
def create_pt_profile(sender, instance, created, **kwargs):
    if created:
        PtProfile.objects.create(user=instance)
