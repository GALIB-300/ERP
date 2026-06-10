# A - Import Required Modules #
from django.apps import AppConfig

# B - Price Event App Configuration #
class PriceEventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'price_event'

    # C - Ready Method to Load Signals #
    def ready(self):
        import price_event.signals
