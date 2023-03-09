from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.project"

    def ready(self):
        try:
            import project.signals  # noqa F401
        except ImportError:
            pass
