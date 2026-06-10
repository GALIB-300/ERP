# A - Import Required Modules #
from django.apps import AppConfig

# B - App Configuration #
class RwcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rwc'

    def ready(self):
        import rwc.signals
