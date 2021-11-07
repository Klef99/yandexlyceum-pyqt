import sqlite3
import hashlib
import os

from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QWidget, QTableView, QApplication

from CustomExceptions import WrongLogin, WrongPassword, UserExists, ShortLogin


class DatabaseHandler:
    def __init__(self, db_name):
        self.database = db_name  # Путь до базы данных
        # Подключение к БД
        self.connection = sqlite3.connect(self.database)
        # Создание курсора
        self.cur = self.connection.cursor()
        # Подключим базу с помощью встроенного в Qt обработчика
        # Зададим тип базы данных
        self.QtDB = QSqlDatabase.addDatabase('QSQLITE')
        # Укажем имя базы данных
        self.QtDB.setDatabaseName(self.database)
        # И откроем подключение
        self.QtDB.open()

    def pass_to_hash(self, password):
        """Функция конвертирует полученный пароль в хеш для хранения в базе данных"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',  # Используемый алгоритм хеширования
            password.encode('utf-8'),  # Конвертируется пароль в байты
            salt,  # Предоставляется соль
            100000  # 100000 итераций SHA-256
        )
        return key.hex(), salt.hex()

    def pass_check(self, password, key, salt):
        key = bytes.fromhex(key)
        salt = bytes.fromhex(salt)
        new_key = hashlib.pbkdf2_hmac(
            'sha256',  # Используемый алгоритм хеширования
            password.encode('utf-8'),  # Конвертируется пароль в байты
            salt,  # Предоставляется соль
            100000  # 100000 итераций SHA-256
        )
        if key == new_key:
            return True
        return False

    def check_login(self, login, password):
        if not self.user_in_db(login):
            raise WrongLogin
        tmp = self.cur.execute("""SELECT passHash, passSalt FROM users WHERE name == ?""", (login,)).fetchall()[0]
        if self.pass_check(password, tmp[0], tmp[1]):
            return True
        raise WrongPassword

    def get_user_id(self, username):
        return self.cur.execute('''SELECT userID FROM users WHERE name == ?''', (username,)).fetchone()[0]

    def user_in_db(self, login):
        if len(self.cur.execute("""SELECT name FROM users WHERE name == ?""", (login,)).fetchall()) != 0:
            return True
        return False

    def register(self, login, password):
        if self.user_in_db(login):
            raise UserExists
        if len(login) < 4:
            raise ShortLogin
        if login and password:
            key, salt = self.pass_to_hash(password)
            self.cur.execute("""INSERT INTO users(name, passHash, passSalt) VALUES(?, ?, ?)""", (login, key, salt,))
            self.connection.commit()
        else:
            raise WrongLogin
        os.mkdir(f'UserBooks/{login}')
        return True


tmp = DatabaseHandler('database.db')
# tmp.register('test', "test")
# print(tmp.check_login('test', 'test'))
