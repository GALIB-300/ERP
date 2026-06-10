# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PriceEventProfile

# B - Signal: Create PriceEventProfile When User Is Created #
@receiver(post_save, sender=User)
def create_price_event_profile(sender, instance, created, **kwargs):
    if created:
        PriceEventProfile.objects.create(user=instance)
