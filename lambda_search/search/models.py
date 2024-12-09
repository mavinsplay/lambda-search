from pathlib import Path
import sqlite3

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from search.encryptor import CellEncryptor, filter_system_tables


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
        _("Имя базы данных"),
        max_length=255,
        unique=True,
    )
    file = models.FileField(
        ("Файл базы данных"),
        upload_to=database_upload_path,
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

    @property
    def path(self):
        """Возвращает путь к файлу базы данных."""
        return self.file.path

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
            encryptor = CellEncryptor(key)
            encryptor.encrypt_database_cells(Path(self.path))
            self.is_encrypted = True
            super().save(update_fields=["is_encrypted"])

        self._update_database_config()

    def delete(self, *args, **kwargs):
        """Удаление базы данных из конфигурации."""
        if Path(self.file.path).exists():
            Path(self.file.path).unlink()

        super().delete(*args, **kwargs)

    def _update_database_config(self):
        """Обновление settings.DATABASES при изменении записей."""

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
        verbose_name = _("База данных")
        verbose_name_plural = _("Базы данных")

    def __str__(self):
        return self.name


class UnifiedDatabaseManager:
    """Менеджер для работы с объединёнными базами данных."""

    def __init__(self):
        key = settings.ENCRYPTION_KEY
        self.encryptor = CellEncryptor(key)

    def _get_active_databases(self):
        """Возвращает список путей активных баз данных."""
        return ManagedDatabase.objects.filter(active=True)

    def search(self, query):
        """
        Ищет информацию во всех активных базах данных.

        :param query: Поисковый запрос (например, имя "Миша").
        :return: Список с результатами поиска по каждой базе данных.
        """
        results = []
        for db in self._get_active_databases():
            db_path = db.path
            result = self._search_in_database(db, db_path, query)
            if result["results"]:
                results.append(result)

        return results

    def _search_in_database(self, db, db_path, query):
        """
        Выполняет поиск в одной базе данных.

        :param db_name: Название базы данных.
        :param db_path: Путь к базе данных.
        :param query: Поисковый запрос.
        :return: Словарь с результатами.
        """
        data = {
            "database": db.name,
            "results": [],
        }

        encrypted_query = self.encryptor.encrypt(query)

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table';",
                )
                tables = filter_system_tables(cursor.fetchall())

                for table_name in tables:
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = [col[1] for col in cursor.fetchall()][1:]

                    for column in columns:
                        cursor.execute(
                            (
                                f"SELECT * FROM {table_name} "
                                f"WHERE {column} LIKE ? LIMIT 10;"
                            ),
                            (f"%{encrypted_query}%",),
                        )
                        rows = cursor.fetchall()

                        if rows:
                            for row in rows:
                                data["results"].append(
                                    {
                                        "table": table_name,
                                        "history": db.history,
                                        "columns": columns,
                                    },
                                )

                cursor.close()

        except sqlite3.DatabaseError as e:
            data["error"] = str(e)

        return data


class UnifiedDatabase:
    """Класс для работы с объединённой моделью."""

    objects = UnifiedDatabaseManager()
