# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import RequisitionProfile

# B - Signal: Create RequisitionProfile When User Is Created #
@receiver(post_save, sender=User)
def create_requisition_profile(sender, instance, created, **kwargs):
    # Step-(B1)-Check if user is newly created #
    if created:
        # Step-(B2)-Create RequisitionProfile linked to the user #
        RequisitionProfile.objects.create(user=instance)
