# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import StcProfile

# B - Signal: Create StcProfile When User Is Created #
@receiver(post_save, sender=User)
def create_stc_profile(sender, instance, created, **kwargs):
    if created:
        StcProfile.objects.create(user=instance)
