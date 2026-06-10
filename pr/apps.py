# A - Import Required Modules #
from django.apps import AppConfig

# B - Pr AppConfig #
class PrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pr"

    # C - Ready Method (Load Signals) #
    def ready(self):
        import pr.signals
