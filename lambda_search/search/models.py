from pathlib import Path
import sqlite3

from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ()


def database_upload_path(instance, filename):
    """Генерирует путь для сохранения файла базы данных."""
    return str(Path("lambda-dbs") / filename)


def validate_database(file_path):
    """Проверяет, что файл является корректной SQLite-базой."""
    try:
        with sqlite3.connect(file_path) as conn:
            conn.execute("SELECT name FROM sqlite_master LIMIT 1;")
    except sqlite3.DatabaseError as e:
        raise ValueError(f"Неверный файл базы данных: {e}")


class ManagedDatabase(models.Model):
    """Модель для хранения информации о базах данных."""

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Имя базы данных"),
    )
    file = models.FileField(
        upload_to=database_upload_path,
        verbose_name=_("Файл базы данных"),
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Активна",
        help_text=_("Определяет, используется ли эта база данных"),
    )

    @property
    def path(self):
        """Возвращает путь к файлу базы данных."""
        return self.file.path

    def save(self, *args, **kwargs):
        """Добавление в настройки Django."""
        super().save(*args, **kwargs)
        validate_database(self.path)
        self._update_database_config()

    def delete(self, *args, **kwargs):
        """Удаление базы данных из конфигурации."""
        if self.file and self.file.path and Path(self.file.path).exists():
            Path(self.file.path).unlink()

        super().delete(*args, **kwargs)

    def _update_database_config(self):
        """Обновление settings.DATABASES при изменении записей."""
        from django.conf import settings

        for db_name in list(settings.DATABASES.keys()):
            if db_name != "default":
                del settings.DATABASES[db_name]

        active_dbs = ManagedDatabase.objects.filter(active=True)
        for db in active_dbs:
            settings.DATABASES[db.name] = {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(db.path),
                "ATOMIC_REQUESTS": False,
                "AUTOCOMMIT": True,
            }

    class Meta:
        verbose_name = "База данных"
        verbose_name_plural = "Базы данных"

    def __str__(self):
        return self.name
