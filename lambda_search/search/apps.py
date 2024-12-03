from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

__all__ = ()


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"
    verbose_name = _("Поиск")

    def ready(self):
        import search.signals  # noqa
