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


class CellEncryptor:
    """Класс для шифрования и дешифрования ячеек базы данных."""

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

    def encrypt_database_cells(self, db_path: Path):
        """Шифрует ячейки базы данных, избегая системных таблиц."""
        conn = sqlite3.connect(db_path)
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
                        encrypted_value = self.encrypt(value)
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
