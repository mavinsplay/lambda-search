from abc import ABC, abstractmethod
import csv
from pathlib import Path
import sqlite3

from django.conf import settings

from search.forms import normalize_search_query

__all__ = ()


def filter_system_tables(all_tables: list) -> list:
    system_tables = {
        "sqlite_sequence",
        "sqlite_stat1",
        "sqlite_stat4",
        "sqlite_stat3",
    }
    return [table[0] for table in all_tables if table[0] not in system_tables]


class DatabaseHandler(ABC):
    def __init__(self, encryptor):
        self.encryptor = encryptor

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def count_rows(self) -> int:
        """Возвращает общее количество строк для обработки"""
        pass

    @abstractmethod
    def encrypt(self, progress_callback):
        """
        Шифрует данные, вызывая progress_callback(processed_rows)
        после обработки каждой строки.
        """
        pass


class SQLiteHandler(DatabaseHandler):
    def __init__(self, db_path: Path, encryptor=None):
        super().__init__(encryptor)
        self.db_path = db_path

    def validate(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            conn.close()
        except sqlite3.Error:
            raise ValueError(
                "Файл не является корректной SQLite базой данных.",
            )

    def count_rows(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = filter_system_tables(cursor.fetchall())
        total = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total += cursor.fetchone()[0]

        conn.close()
        return total

    def encrypt(self, progress_callback):
        from search.models import Data, ManagedDatabase

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = filter_system_tables(cursor.fetchall())
        processed = 0

        managed_database = ManagedDatabase.objects.get(
            file__endswith=self.db_path.name,
        )
        batch = []

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [col[1] for col in cursor.fetchall()]
            cursor.execute(f"SELECT rowid, * FROM {table};")
            rows = cursor.fetchall()

            for row in rows:
                row_id = row[0]
                for idx, value in enumerate(row[1:]):
                    if isinstance(value, str):
                        encrypted_value = self.encryptor.encrypt(
                            normalize_search_query(value),
                        )
                        batch.append(
                            Data(
                                database=managed_database,
                                user_index=row_id,
                                column_name=columns[idx],
                                value=encrypted_value[:255],
                            ),
                        )

                if len(batch) >= settings.BATCH_SIZE:
                    Data.objects.bulk_create(batch)
                    batch.clear()

                processed += 1
                progress_callback(processed)

        if batch:
            Data.objects.bulk_create(batch)
            batch.clear()

        conn.close()

    def read_data(self, n):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = filter_system_tables(cursor.fetchall())

        data = {}
        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [column[1] for column in cursor.fetchall()]

            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?;", (n,))
            rows = cursor.fetchall()

            data[table_name] = {"columns": columns, "rows": rows}

        conn.close()
        return data


class CSVHandler(DatabaseHandler):
    def __init__(self, csv_path: Path, encryptor=None):
        super().__init__(encryptor)
        self.csv_path = csv_path

    def validate(self):
        try:
            with self.csv_path.open("r", newline="", encoding="utf-8") as file:
                csv.reader(file)
        except Exception as e:
            raise ValueError("Файл не является корректным CSV: " + str(e))

    def count_rows(self) -> int:
        with self.csv_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)

        return len(rows) - 1 if rows else 0

    def encrypt(self, progress_callback):
        from search.models import Data, ManagedDatabase

        with self.csv_path.open("r", newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            rows = list(reader)

        headers = rows[0] if rows else []
        processed = 0
        batch = []
        managed_database = ManagedDatabase.objects.get(
            file__endswith=self.csv_path.name,
        )

        for row_index, row in enumerate(rows[1:], start=1):
            for col_index, value in enumerate(row):
                if value:
                    encrypted_value = self.encryptor.encrypt(
                        normalize_search_query(value),
                    )
                    batch.append(
                        Data(
                            database=managed_database,
                            user_index=row_index,
                            column_name=(
                                headers[col_index]
                                if headers
                                else f"Column {col_index+1}"
                            ),
                            value=encrypted_value[:255],
                        ),
                    )

            if len(batch) >= settings.BATCH_SIZE:
                Data.objects.bulk_create(batch)
                batch.clear()

            processed += 1
            progress_callback(processed)

        if batch:
            Data.objects.bulk_create(batch)
            batch.clear()

    def read_data(self, n):
        with self.csv_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)

        headers = rows[0] if rows else []
        limited_rows = rows[1 : n + 1]  # noqa
        return {
            f"{self.csv_path.name}": {
                "columns": headers,
                "rows": limited_rows,
            },
        }
