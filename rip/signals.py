# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import RipProfile

# B - Signal: Create RipProfile When User Is Created #
@receiver(post_save, sender=User)
def create_rip_profile(sender, instance, created, **kwargs):
    if created:
        RipProfile.objects.create(user=instance)
