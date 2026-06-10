# A - Import Required Modules #
from django.apps import AppConfig

# B - Stc AppConfig #
class StcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stc"

    # C - Ready Method (Load Signals) #
    def ready(self):
        import stc.signals
