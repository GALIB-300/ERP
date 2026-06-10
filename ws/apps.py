from django.apps import AppConfig

class WsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ws'

    def ready(self):
        import ws.signals



    
