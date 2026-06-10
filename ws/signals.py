# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import WsProfile

# B - Signal: Create WsProfile When User Is Created #
@receiver(post_save, sender=User)
def create_ws_profile(sender, instance, created, **kwargs):
    if created:
        WsProfile.objects.create(user=instance)
