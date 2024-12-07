import sqlite3
from pathlib import Path

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
        verbose_name = _("База данных")
        verbose_name_plural = _("Базы данных")

    def __str__(self):
        return self.name


class UnifiedDatabaseManager:
    """Менеджер для работы с объединёнными базами данных."""

    def __init__(self):
        self.databases = self._get_active_databases()

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
        for db in self.databases:
            db_path = db.path
            result = self._search_in_database(db.name, db_path, query)
            results.append(result)

        return results

    def _search_in_database(self, db_name, db_path, query):
        """
        Выполняет поиск в одной базе данных.

        :param db_name: Название базы данных.
        :param db_path: Путь к базе данных.
        :param query: Поисковый запрос.
        :return: Словарь с результатами.
        """
        data = {
            "database": db_name,
            "results": [],
        }
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table';",
                )
                tables = cursor.fetchall()

                for (table_name,) in tables:
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = [col[1] for col in cursor.fetchall()]

                    # Выполняем поиск в таблице
                    for column in columns:
                        cursor.execute(
                            (
                                f"SELECT * FROM "
                                f"{table_name} WHERE {column} LIKE ? LIMIT 10;"
                            ),
                            (f"%{query}%",),
                        )
                        rows = cursor.fetchall()
                        if rows:
                            data["results"].append(
                                {
                                    "table": table_name,
                                    "column": column,
                                    "rows": rows,
                                },
                            )
        except sqlite3.DatabaseError as e:
            data["error"] = str(e)

        return data

    def format_results(self, results):
        """
        Форматирует результаты поиска в виде таблицы с булевыми значениями.

        :param results: Сырые данные из `_search_in_database`.
        :return: Отформатированные данные.
        """
        formatted = []
        for result in results:
            for entry in result["results"]:
                formatted.append(
                    {
                        "database": result["database"],
                        "table": entry["table"],
                        "column": entry["column"],
                        "found": bool(entry["rows"]),
                    },
                )

        return formatted


class UnifiedDatabase:
    """Класс для работы с объединённой моделью."""

    objects = UnifiedDatabaseManager()
