from abc import ABC, abstractmethod
import csv
from pathlib import Path
import sqlite3

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
    """Абстрактный класс для обработки баз данных."""

    def __init__(self, encryptor):
        self.encryptor = encryptor

    @abstractmethod
    def validate(self):
        """Валидирует файл базы данных."""
        pass

    @abstractmethod
    def read_data(self):
        """Читает содержимое базы данных SQLite без расшифровки."""
        pass

    def encrypt(self):
        """Шифрует содержимое базы данных."""
        pass


class SQLiteHandler(DatabaseHandler):
    """Класс для обработки SQLite баз данных."""

    def __init__(self, db_path: Path, encryptor=None):
        super().__init__(encryptor)
        self.db_path = db_path

    def validate(self):
        """Проверяет, является ли файл SQLite базой данных."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            conn.close()
        except sqlite3.Error:
            raise ValueError(
                "Файл не является корректной SQLite базой данных.",
            )

    def encrypt(self):
        from search.models import Data, ManagedDatabase

        """Шифрует содержимое базы данных и записывает в таблицу Data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_to_encrypt = filter_system_tables(cursor.fetchall())

        managed_database = ManagedDatabase.objects.get(
            file__endswith=self.db_path.name,
        )

        for table_name in tables_to_encrypt:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [column[1] for column in cursor.fetchall()]

            cursor.execute(f"SELECT rowid, * FROM {table_name};")
            rows = cursor.fetchall()

            for row in rows:
                row_id = row[0]
                encrypted_row = []
                for idx, value in enumerate(row[1:]):
                    if isinstance(value, str):
                        encrypted_value = self.encryptor.encrypt(value)
                        encrypted_row.append(encrypted_value)

                        data_record = Data(
                            database=managed_database,
                            user_index=row_id,
                            column_name=columns[idx],
                            value=encrypted_value[:255],
                        )
                        data_record.save()
                    else:
                        encrypted_row.append(value)

                set_clause = ", ".join([f"{column} = ?" for column in columns])
                cursor.execute(
                    f"UPDATE {table_name} SET {set_clause} WHERE rowid = ?",
                    (*encrypted_row, row_id),
                )

        conn.commit()
        conn.close()

    def read_data(self, n):
        """Читает содержимое базы данных SQLite без расшифровки."""
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
    """Класс для обработки CSV файлов."""

    def __init__(self, csv_path: Path, encryptor=None):
        super().__init__(encryptor)
        self.csv_path = csv_path

    def validate(self):
        """Проверяет корректность CSV файла."""
        try:
            with self.csv_path.open("r", newline="", encoding="utf-8") as file:
                csv.reader(file)
        except Exception as e:
            raise ValueError("Файл не является корректным CSV: " + str(e))

    def encrypt(self):
        """Шифрует содержимое CSV файла."""
        from search.models import Data, ManagedDatabase

        with self.csv_path.open("r", newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            rows = list(reader)

        headers = rows[0] if rows else None

        managed_database = ManagedDatabase.objects.get(
            file__endswith=self.csv_path.name,
        )

        data_objects = []  # Список для хранения объектов Data
        with self.csv_path.open("w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)

            if headers:
                writer.writerow(headers)

            for row_index, row in enumerate(rows[1:], start=1):
                encrypted_row = []
                for col_index, value in enumerate(row):
                    if value:
                        encrypted_value = self.encryptor.encrypt(value)
                        encrypted_row.append(encrypted_value)

                        # Создаем объект Data и добавляем его в список
                        data_objects.append(
                            Data(
                                database=managed_database,
                                user_index=row_index,
                                column_name=(
                                    headers[col_index]
                                    if headers
                                    else f"Column {col_index + 1}"
                                ),
                                value=encrypted_value[:255],
                            ),
                        )
                    else:
                        encrypted_row.append(value)

                writer.writerow(encrypted_row)

        # Используем bulk_create для массового создания объектов
        Data.objects.bulk_create(data_objects)

    def read_data(self, n):
        """Читает первые n записей из CSV файла без расшифровки."""
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
