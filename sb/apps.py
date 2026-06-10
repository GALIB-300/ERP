# A - Import Required Modules #
from django.apps import AppConfig

# B - Sb AppConfig #
class SbConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sb"

    # C - Ready Method (Load Signals) #
    def ready(self):
        import sb.signals   # ✅ updated to sb-app

