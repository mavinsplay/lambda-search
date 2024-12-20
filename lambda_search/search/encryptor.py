from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from search.handlers import CSVHandler, SQLiteHandler

__all__ = ()


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
