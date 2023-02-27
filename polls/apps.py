from django.apps import AppConfig


class PollsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "polls"

    def ready(self):
        import polls.signals

        x = polls.signals  # this is to satisfy flake8's no unused import
