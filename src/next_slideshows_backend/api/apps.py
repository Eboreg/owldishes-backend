from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "next_slideshows_backend.api"

    def ready(self):
        from next_slideshows_backend.api import signals
