from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

__all__ = ()


class HistoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "history"
    verbose_name = _("История")
