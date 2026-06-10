# A - Import Required Modules #
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProposalProfile

# B - Signal: Create ProposalProfile When User Is Created #
@receiver(post_save, sender=User)
def create_proposal_profile(sender, instance, created, **kwargs):
    if created:
        ProposalProfile.objects.create(user=instance)
