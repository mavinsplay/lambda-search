from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ()


DEFAULT_STRING_LIMIT = 50


class ManagedDatabase(models.Model):

    name = models.CharField(
        _("Имя базы данных"),
        max_length=255,
        unique=True,
    )

    history = models.TextField(
        _("История"),
        help_text=_("Краткая история об утечке (не более 500 символов)"),
        default=_("История об этой базе не найдена"),
        max_length=500,
        blank=True,
        null=True,
    )

    active = models.BooleanField(
        _("Активна"),
        help_text=_("Определяет, используется ли эта база данных"),
        default=False,
    )
    is_encrypted = models.BooleanField(
        _("Зашифрована"),
        default=False,
    )
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
        null=True,
    )

    class Meta:
        verbose_name = _("База данных")
        verbose_name_plural = _("Базы данных")

    def __str__(self):
        return self.name[:DEFAULT_STRING_LIMIT]


class DataMagager(models.Manager):
    def _active(self):
        return (
            self.get_queryset()
            .filter(
                database__active=True,
                database__is_encrypted=True,
            )
            .order_by(
                Data.database.field.name,
            )
        )

    def _search_value(self, input_data):
        return (
            self._active()
            .filter(
                value=input_data,
            )
            .values(
                Data.database.field.name,
                Data.user_index.field.name,
            )
        ).distinct()

    def _search(self, indexes):
        query = models.Q()
        for indexes in indexes:
            query |= models.Q(
                database_id=indexes["database"],
                user_index=indexes["user_index"],
            )

        return (
            self._active()
            .filter(
                query,
            )
            .order_by(
                Data.database.field.name,
                Data.user_index.field.name,
            )
            .only(
                Data.database.field.name,
                Data.user_index.field.name,
            )
        )

    def search(self, input_data):
        return (
            self._search(self._search_value(input_data))
            .select_related(Data.database.field.name)
            .only(
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.name.field.name}",
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.history.field.name}",
                Data.database.field.name,
                Data.user_index.field.name,
                Data.column_name.field.name,
            )
        )


class Data(models.Model):
    objects = DataMagager()
    database = models.ForeignKey(
        ManagedDatabase,
        on_delete=models.CASCADE,
        related_name="data",
        verbose_name=_("Имя базы данных"),
    )
    user_index = models.IntegerField(
        _("Индекс пользователя"),
    )
    column_name = models.CharField(
        _("Название колонки"),
        max_length=255,
    )
    value = models.CharField(
        _("Значение"),
        max_length=255,
    )

    class Meta:
        verbose_name = _("Данные")
        verbose_name_plural = _("Данные")

    def __str__(self):
        return str(self.pk)[:DEFAULT_STRING_LIMIT]
