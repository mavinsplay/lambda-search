from pathlib import Path

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from search.encryptor import UnifiedEncryptor

__all__ = ()


DEFAULT_STRING_LIMIT = 50


def database_upload_path(instance, filename):
    """Генерирует путь для сохранения файла базы данных."""
    return str(Path("lambda-dbs") / filename)


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
            self.encrypt_database()

    def encrypt_database(self):
        """Encrypt the database file."""
        key = settings.ENCRYPTION_KEY
        encryptor = UnifiedEncryptor(key)
        encryptor.encrypt_database_cells(file_path=Path(self.file.path))
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
        return self.name[:DEFAULT_STRING_LIMIT]


class DataMagager(models.Manager):
    def _active(self):
        """
        Возвращает активные и зашифрованные базы данных.
        """
        return (
            self.get_queryset()
            .filter(
                **{
                    f"{Data.database.field.name}__"
                    f"{ManagedDatabase.active.field.name}": True,
                    f"{Data.database.field.name}__"
                    f"{ManagedDatabase.is_encrypted.field.name}": True,
                },
            )
            .order_by(
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.name.field.name}",
            )
        )

    def _search_value(self, input_data):
        """
        Ищет значения, соответствующие введённым данным,
        в активных и зашифрованных базах данных.
        """
        return (
            self._active()
            .filter(**{f"{Data.value.field.name}__iexact": input_data})
            .values(
                Data.database.field.name,
                Data.user_index.field.name,
            )
            .distinct()
        )

    def _search(self, indexes):
        """
        Ищет данные в активных базах данных на основе индексов.
        """
        query = models.Q()
        for index in indexes:
            query |= models.Q(
                **{
                    Data.database.field.name: index[Data.database.field.name],
                    Data.user_index.field.name: index[
                        Data.user_index.field.name
                    ],
                },
            )

        if not indexes:
            return self.none()

        return (
            self._active()
            .filter(query)
            .order_by(
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.name.field.name}",
                Data.user_index.field.name,
            )
        )

    def search(self, input_data):
        """
        Основной метод поиска. Находит все совпадения для указанного значения
        и возвращает соответствующие результаты.
        """
        indexes = list(self._search_value(input_data))

        if not indexes:
            return self.none()

        return (
            self._search(indexes)
            .select_related(Data.database.field.name)
            .only(
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.name.field.name}",
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.history.field.name}",
                Data.database.field.name,
                Data.user_index.field.name,
                Data.column_name.field.name,
                Data.value.field.name,
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
