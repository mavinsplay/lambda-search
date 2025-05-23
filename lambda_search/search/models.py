from pathlib import Path

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from search.encryptor import UnifiedEncryptor
import search.managers

__all__ = ()


DEFAULT_STRING_LIMIT = 50


def database_upload_path(instance, filename):
    """
    Генерирует безопасный путь для загрузки файла базы данных
    """
    ext = Path(filename).suffix
    safe_name = slugify(instance.name)
    return f"protected/databases/{safe_name}{ext}"


class ManagedDatabase(models.Model):

    name = models.CharField(
        _("Имя базы данных"),
        max_length=255,
        unique=True,
    )
    file = models.FileField(
        ("Файл базы данных"),
        upload_to=database_upload_path,
        blank=True,
        validators=[FileExtensionValidator(["csv", "sqlite", "db"])],
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
    encryption_started = models.BooleanField(
        _("шифрование запущено"),
        default=False,
    )
    progress_task_id = models.CharField(
        _("ID задачи шифрования"),
        max_length=255,
        blank=True,
        null=True,
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
        super().save(*args, **kwargs)
        if not self.is_encrypted and self.file and not self.encryption_started:
            from search.tasks import encrypt_database_task

            try:
                from django.db import transaction

                self.encryption_started = True
                ManagedDatabase.objects.filter(pk=self.pk).update(
                    encryption_started=True,
                )
                transaction.on_commit(
                    lambda: encrypt_database_task.delay(self.pk),
                )
            except Exception as e:
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    f"Ошибка при обработке базы данных: {str(e)}",
                )

    def encrypt_database(self):
        key = settings.ENCRYPTION_KEY
        encryptor = UnifiedEncryptor(key, file_path=Path(self.file.path))
        encryptor.encrypt_database_cells()
        self.is_encrypted = True
        super().save(update_fields=["is_encrypted"])

    def delete(self, *args, **kwargs):
        if self.file and Path(self.file.path).exists():
            Path(self.file.path).unlink()

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _("База данных")
        verbose_name_plural = _("Базы данных")

    def __str__(self):
        return self.name[:DEFAULT_STRING_LIMIT]


class Data(models.Model):
    objects = search.managers.DataMagager()
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
        unique_together = ("database", "user_index", "column_name", "value")
        verbose_name = _("Данные")
        verbose_name_plural = _("Данные")

    def __str__(self):
        return str(self.pk)[:DEFAULT_STRING_LIMIT]
