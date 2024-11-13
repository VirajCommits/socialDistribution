from django.apps import AppConfig


class BackendAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backendApp"

    def ready(self):
        from .tasks import start_github_fetcher_thread

        start_github_fetcher_thread()
