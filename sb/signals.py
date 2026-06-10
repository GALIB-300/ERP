# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import SbProfile   # ✅ updated to sb-app

# B - Signal: Create SbProfile When User Is Created #
@receiver(post_save, sender=User)
def create_sb_profile(sender, instance, created, **kwargs):
    if created:
        SbProfile.objects.create(user=instance)
