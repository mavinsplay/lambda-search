from abc import ABC, abstractmethod
import csv
from pathlib import Path
import sqlite3

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

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
        """Шифрует содержимое базы данных SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_to_encrypt = filter_system_tables(cursor.fetchall())

        for table_name in tables_to_encrypt:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]

            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            for row in rows:
                encrypted_row = []
                for idx, value in enumerate(row):
                    if isinstance(value, str):
                        encrypted_value = self.encryptor.encrypt(value)
                        encrypted_row.append(encrypted_value)
                    else:
                        encrypted_row.append(value)

                set_clause = ", ".join(
                    [f"{column} = ?" for column in column_names],
                )

                cursor.execute(
                    f"UPDATE {table_name} SET {set_clause} WHERE rowid = ?",
                    (*encrypted_row, row[0]),
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
        with self.csv_path.open("r", newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            rows = list(reader)

        with self.csv_path.open("w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)

            headers = rows[0] if rows else None
            if headers:
                writer.writerow(headers)

            for row in rows[1:]:
                encrypted_row = [
                    self.encryptor.encrypt(cell) if cell else cell
                    for cell in row
                ]
                writer.writerow(encrypted_row)

    def read_data(self, n):
        """Читает первые n записей из CSV файла без расшифровки."""
        with self.csv_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)

        headers = rows[0] if rows else []
        limited_rows = rows[1 : n + 1]
        return {
            f"{self.csv_path.name}": {
                "columns": headers,
                "rows": limited_rows,
            },
        }


class CellEncryptor:
    """Класс для шифрования и дешифрования ячеек."""

    def __init__(self, key: bytes):
        self.key = key
        self.iv = key[:16]

    def encrypt(self, data: str) -> str:
        """Шифрует строку с фиксированным IV."""
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(self.iv),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        padded_data = self._pad(data.encode())
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted.hex()

    def decrypt(self, encrypted_data: str) -> str:
        """Дешифрует строку с фиксированным IV."""
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(self.iv),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        decrypted = (
            decryptor.update(bytes.fromhex(encrypted_data))
            + decryptor.finalize()
        )
        return self._unpad(decrypted).decode()

    def _pad(self, data: bytes, block_size=16):
        padding_len = block_size - len(data) % block_size
        return data + bytes([padding_len] * padding_len)

    def _unpad(self, data: bytes):
        padding_len = data[-1]
        return data[:-padding_len]


class BaseHandlerManager:
    """Базовый класс для управления обработчиками файлов."""

    def __init__(self):
        self.handlers = {
            ".sqlite": SQLiteHandler,
            ".db": SQLiteHandler,
            ".csv": CSVHandler,
        }

    def get_handler(self, file_path: Path, encryptor=None):
        """Получает обработчик для указанного файла."""
        handler_class = self.handlers.get(file_path.suffix)
        if not handler_class:
            raise ValueError("Неподдерживаемый формат файла.")

        return (
            handler_class(file_path, encryptor)
            if encryptor
            else handler_class(file_path)
        )


class UnifiedEncryptor(BaseHandlerManager):
    """Обработчик для автоматической обработки SQLite и CSV."""

    def __init__(self, key: bytes):
        super().__init__()
        self.encryptor = CellEncryptor(key)

    def encrypt_database_cells(self, file_path: Path):
        """Определяет тип базы данных и шифрует её содержимое."""
        handler = self.get_handler(file_path, self.encryptor)
        handler.validate()
        handler.encrypt()


class DbsReader(BaseHandlerManager):
    """Читает данные из базы данных без расшифровки."""

    def __init__(self):
        super().__init__()

    def read_data(self, file_path: Path, n: int):
        """Читает содержимое базы данных."""
        handler = self.get_handler(file_path)
        handler.validate()
        return handler.read_data(n)
