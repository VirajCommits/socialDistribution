from django.apps import AppConfig

class BackendAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backendApp"

    def ready(self):
        # Import and start the scheduler here
        from .tasks import start_scheduler

        start_scheduler()
