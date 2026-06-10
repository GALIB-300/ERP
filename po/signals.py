# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PoProfile

# B - Signal: Create PoProfile When User Is Created #
@receiver(post_save, sender=User)
def create_po_profile(sender, instance, created, **kwargs):
    # Step-(B1)-Check if user is newly created #
    if created:
        # Step-(B2)-Create PoProfile linked to the user #
        PoProfile.objects.create(user=instance)
