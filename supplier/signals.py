# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import SupplierProfile

# B - Signal: Create SupplierProfile When User Is Created #
@receiver(post_save, sender=User)
def create_supplier_profile(sender, instance, created, **kwargs):
    if created:
        SupplierProfile.objects.create(user=instance)
