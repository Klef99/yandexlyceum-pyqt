import hashlib
import os
import sqlite3

from PyQt5.QtSql import QSqlDatabase

from CustomExceptions import *


class DatabaseHandler:
    def __init__(self, db_name):
        self.database = db_name  # Путь до базы данных
        # Подключение к БД
        self.connection = sqlite3.connect(self.database)
        # Создание курсора
        self.cur = self.connection.cursor()
        # Подключим базу с помощью встроенного в Qt обработчика
        self.QtDB = QSqlDatabase.addDatabase("QSQLITE")  # Зададим тип базы данных
        self.QtDB.setDatabaseName(self.database)  # Укажем имя базы данных
        self.QtDB.open()  # И откроем подключение

    def pass_to_hash(self, password):
        """Функция конвертирует полученный пароль в хеш для хранения в базе данных"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            "sha256",  # Используемый алгоритм хеширования
            password.encode("utf-8"),  # Конвертируется пароль в байты
            salt,  # Предоставляется соль
            100000,  # 100000 итераций SHA-256
        )
        return key.hex(), salt.hex()

    def pass_check(self, password, key, salt):
        key = bytes.fromhex(key)
        salt = bytes.fromhex(salt)
        new_key = hashlib.pbkdf2_hmac(
            "sha256",  # Используемый алгоритм хеширования
            password.encode("utf-8"),  # Конвертируется пароль в байты
            salt,  # Предоставляется соль
            100000,  # 100000 итераций SHA-256
        )
        if key == new_key:
            return True
        return False

    def check_login(self, login, password):
        if not self.user_in_db(login):
            raise WrongLogin
        tmp = self.cur.execute(
            """SELECT passHash, passSalt FROM users WHERE name == ?""", (login,)
        ).fetchall()[0]
        if self.pass_check(password, tmp[0], tmp[1]):
            return True
        raise WrongPassword

    def get_user_id(self, username):
        return self.cur.execute(
            """SELECT userID FROM users WHERE name == ?""", (username,)
        ).fetchone()[0]

    def get_book_id(self, user_id, bookName):
        uid = self.cur.execute(
            """SELECT bookID from books WHERE userID == ? AND bookName like ?""",
            (
                user_id,
                bookName,
            ),
        ).fetchall()
        if uid:
            return uid[0][0]
        return ""

    def user_in_db(self, login):
        if (
            len(
                self.cur.execute(
                    """SELECT name FROM users WHERE name == ?""", (login,)
                ).fetchall()
            )
            != 0
        ):
            return True
        return False

    def register(self, login, password):
        if self.user_in_db(login):
            raise UserExists
        if len(login) < 4:
            raise ShortLogin
        if login and password:
            key, salt = self.pass_to_hash(password)
            self.cur.execute(
                """INSERT INTO users(name, passHash, passSalt) VALUES(?, ?, ?)""",
                (
                    login,
                    key,
                    salt,
                ),
            )
            self.connection.commit()
        else:
            raise WrongLogin
        os.mkdir(f"UserBooks/{login}")
        return True

    def check_tag(self, tag):
        if tag in self.get_tags():
            return True
        return False

    def get_tags(self):
        tags = self.cur.execute(
            """SELECT name FROM PRAGMA_TABLE_INFO('tags')"""
        ).fetchall()
        tags = [i[0] for i in tags]
        del tags[0]
        return tags

    def create_tag(self, tag):
        self.cur.execute(f"""ALTER TABLE tags ADD COLUMN {tag} DEFAULT (0)""")
        return True

    def remove_tag(self, book_id, tag):
        self.cur.execute(f"""UPDATE tags SET {tag} = 0 WHERE bookid = ?""", (book_id,))
        tags_list = self.get_book_tags("", "", book_id=book_id)
        del tags_list[tags_list.index(tag)]
        tags_list = ", ".join(tags_list)
        self.cur.execute(
            f"""UPDATE books SET tag = '{tags_list}' WHERE bookid = ?""", (book_id,)
        )
        self.connection.commit()

    def add_book(self, user_id, book_name, author, description, tag, lang, path):
        tmp_tag = tag.split(", ")
        for i in tmp_tag:
            if not self.check_tag(i):
                self.create_tag(i)
        self.cur.execute(
            """INSERT INTO books(userID, bookName, Author, description, tag, lang, path) VALUES(?, ?, ?, ?, ?, ?, ?)""",
            (user_id, book_name, author, description, tag, lang, path),
        )
        quest_str = ", ".join([i for i in tmp_tag])
        self.cur.execute(
            f"""INSERT INTO tags({quest_str}) VALUES({', '.join(['1' for _ in range(len(tmp_tag))])})"""
        )
        self.connection.commit()

    def del_book(self, path):
        book_id = self.cur.execute(
            """SELECT bookID from books WHERE path like ?""", (path,)
        ).fetchall()[0][0]
        self.cur.execute(f"""DELETE FROM books WHERE bookID == {book_id}""")
        self.cur.execute(f"""DELETE FROM tags WHERE bookID == {book_id}""")
        self.connection.commit()

    def get_user_books(self, login):
        user_id = self.get_user_id(login)
        result = self.cur.execute(
            """SELECT bookName from books WHERE userID == ?""", (user_id,)
        ).fetchall()
        result = [i[0] for i in result]
        return result

    def check_book_id(self, login, book, book_id=""):
        if book_id:
            book_id = book_id
        else:
            book_id = self.get_book_id(self.get_user_id(login), book)
        return book_id

    def get_book_tags(self, login, book, book_id=""):
        book_id = self.check_book_id(login, book, book_id)
        res = self.cur.execute(
            """SELECT tag from books WHERE bookID == ?""", (book_id,)
        ).fetchall()[0][0]
        if not res:
            return []
        return res.split(", ")

    def set_book_tags(self, login, book, tags, book_id=""):
        book_id = self.check_book_id(login, book, book_id)
        tags = ", ".join(tags)
        self.cur.execute(
            f"""UPDATE books SET tag = '{tags}' WHERE bookID == ?""", (book_id,)
        )
        self.connection.commit()

    def get_booklist_tags(self, login, books):
        res = []
        for i in books:
            res.extend(self.get_book_tags(login, i))
        return list(set(res))

    def get_book_path(self, user_id, title):
        return self.cur.execute(
            """SELECT path from books WHERE UserID == ? AND bookName like ?""",
            (
                user_id,
                title,
            ),
        ).fetchall()[0][0]

    def get_tag_value(self, login, book, tag, book_id=""):
        book_id = self.check_book_id(login, book, book_id)
        return self.cur.execute(
            f"""SELECT {tag} FROM tags WHERE bookID == ?""", (book_id,)
        ).fetchall()[0][0]

    def link_tag(self, login, book, tag, book_id=""):
        book_id = self.check_book_id(login, book, book_id)
        tags = self.get_book_tags(login, book)
        tags.append(tag)
        self.set_book_tags(login, book, tags)
        self.cur.execute(
            f"""UPDATE tags SET {tag} == 1 WHERE bookID == ?""", (book_id,)
        )
        self.connection.commit()
