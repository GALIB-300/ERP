# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import RbpProfile

# B - Signal: Create RbpProfile When User Is Created #
@receiver(post_save, sender=User)
def create_rbp_profile(sender, instance, created, **kwargs):
    if created:
        RbpProfile.objects.create(user=instance)
