from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from search.encryptor import UnifiedEncryptor


__all__ = ()


def database_upload_path(instance, filename):
    """Генерирует путь для сохранения файла базы данных."""
    return str(Path("lambda-dbs") / filename)


class ManagedDatabase(models.Model):
    """Модель для хранения информации о базах данных."""

    name = models.CharField(
        _("Имя базы данных"),
        max_length=255,
        unique=True,
    )
    file = models.FileField(
        ("Файл базы данных"),
        upload_to=database_upload_path,
        blank=True,
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

    def save(self, *args, **kwargs):
        """Добавление в настройки Django с учётом шифрования."""
        is_new = self.pk is None
        if not is_new:
            old_instance = ManagedDatabase.objects.get(pk=self.pk)
            file_changed = old_instance.file != self.file

            if file_changed:
                self.is_encrypted = False

        super().save(*args, **kwargs)

        if not self.is_encrypted:
            key = settings.ENCRYPTION_KEY
            encryptor = UnifiedEncryptor(key)
            encryptor.encrypt_database_cells(Path(self.file.path))
            self.is_encrypted = True
            super().save(update_fields=["is_encrypted"])

    def delete(self, *args, **kwargs):
        """Удаление базы данных из конфигурации."""
        if Path(self.file.path).exists():
            Path(self.file.path).unlink()

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _("База данных")
        verbose_name_plural = _("Базы данных")

    def __str__(self):
        return self.name


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
            .only(
                Data.database.field.name,
                Data.user_index.field.name,
            )
        )

    def _search(self, indexes):
        return (
            self._active()
            .filter(
                database_id=indexes.database,
                user_index=indexes.user_index,
            )
            .order_by(
                Data.column_name.field.name,
            )
            .values(
                Data.column_name.field.name,
            )
        )

    def search(self, input_data):
        return self._search(self._search_value(input_data))


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
        return self.value
