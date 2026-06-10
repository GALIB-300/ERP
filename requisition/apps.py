from django.apps import AppConfig

class RequisitionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'requisition'

    def ready(self):
        import requisition.signals
