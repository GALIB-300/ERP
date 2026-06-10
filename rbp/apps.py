# A - Import Required Modules #
from django.apps import AppConfig

# B - Rbp AppConfig #
class RbpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rbp"

    # C - Ready Method (Load Signals) #
    def ready(self):
        import rbp.signals
