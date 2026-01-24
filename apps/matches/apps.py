from django.apps import AppConfig


class MatchesConfig(AppConfig):
    name = "apps.matches"

    def ready(self):
        # Importamos los signals para que se registren
        import apps.matches.signals  # noqa: F401
