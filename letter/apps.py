from django.apps import AppConfig

class LetterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'letter'

    def ready(self):
        import letter.signals

