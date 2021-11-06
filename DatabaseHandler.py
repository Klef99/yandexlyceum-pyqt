import sqlite3
import hashlib
import os

class DatabaseHandler:
    def __init__(self):
        self.database = 'database.db' # Путь до базы данных

    def pass_hashing(self, passw):
        """Функция конвертирует полученный пароль в хеш для хранения в базе данных"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',  # Используемый алгоритм хеширования
            passw.encode('utf-8'),  # Конвертируется пароль в байты
            salt,  # Предоставляется соль
            100000  # 100000 итераций SHA-256
        )
        return salt, key