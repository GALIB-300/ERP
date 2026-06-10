from django.apps import AppConfig

class CastingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'casting'

    def ready(self):
        import casting.signals
