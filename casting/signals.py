# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CastingProfile

# B - Signal: Create CastingProfile When User Is Created #
@receiver(post_save, sender=User)
def create_casting_profile(sender, instance, created, **kwargs):
    if created:
        CastingProfile.objects.create(user=instance)
