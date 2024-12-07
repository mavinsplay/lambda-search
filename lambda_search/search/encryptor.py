import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet

__all__ = ()


class DatabaseEncryptor:
    """Класс для шифрования и дешифрования баз данных."""

    def __init__(self, key: bytes):
        """
        :param key: Ключ шифрования (должен быть безопасно сохранён).
        """
        self.cipher = Fernet(key)

    def encrypt_file(self, file_path: str):
        """Шифрует файл."""
        path = Path(file_path)
        encrypted_path = path.with_suffix(".encrypted")
        with Path.open(file_path, "rb") as f:
            data = f.read()

        encrypted_data = self.cipher.encrypt(data)
        with Path.open(encrypted_path, "wb") as f:
            f.write(encrypted_data)

        path.unlink()
        return encrypted_path

    def decrypt_file(self, file_path: str):
        """Дешифрует файл."""
        path = Path(file_path)
        decrypted_path = path.with_suffix(".sqlite")
        with Path.open(file_path, "rb") as f:
            encrypted_data = f.read()

        decrypted_data = self.cipher.decrypt(encrypted_data)
        with Path.open(decrypted_path, "wb") as f:
            f.write(decrypted_data)

        return decrypted_path


class EncryptedDatabaseManager:
    """Менеджер для работы с зашифрованными базами данных."""

    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)

    def query_encrypted_database(
        self,
        encrypted_path: str,
        query: str,
        params=None,
    ):
        """
        Выполняет запрос к зашифрованной базе данных.
        Дешифрует базу на лету, выполняет запрос, затем удаляет временный файл.

        :param encrypted_path: Путь к зашифрованной базе.
        :param query: SQL-запрос.
        :param params: Параметры запроса.
        :return: Результаты выполнения запроса.
        """
        encrypted_file = Path(encrypted_path)
        decrypted_file = encrypted_file.with_suffix(".temp.sqlite")

        with Path.open(encrypted_file, "rb") as f:
            encrypted_data = f.read()

        decrypted_data = self.cipher.decrypt(encrypted_data)
        with Path.open(decrypted_file, "wb") as f:
            f.write(decrypted_data)

        results = []
        try:
            with sqlite3.connect(decrypted_file) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                results = cursor.fetchall()
        finally:
            if decrypted_file.exists():
                decrypted_file.unlink()

        return results
