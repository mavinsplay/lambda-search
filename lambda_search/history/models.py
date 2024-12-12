from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


__all__ = ()


class QueryHistory(models.Model):
    """
    Модель для хранения истории запросов.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="query_histories",
        verbose_name=_("Пользователь"),
        help_text=_("Пользователь, которому принадлежит эта история"),
    )
    query = models.CharField(
        _("Запрос"),
        max_length=255,
    )
    created_at = models.DateTimeField(
        _("Дата запроса"),
        auto_now_add=True,
    )
    database = models.CharField(
        _("База данных"),
        max_length=255,
    )
    result = models.JSONField(
        _("Результаты"),
        help_text=_("Результаты поиска в формате JSON"),
    )

    class Meta:
        verbose_name = _("История запроса")
        verbose_name_plural = _("История запросов")

    def __str__(self):
        return f"{self.query} ({self.created_at})"
