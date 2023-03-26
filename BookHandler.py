import os
import shutil

import ebookmeta

from CustomExceptions import *
from DatabaseHandler import DatabaseHandler


class BookHandler:
    def __init__(self, login):
        self.support_format = ["fb2", "epub"]
        if login:
            self.user_login = login
        else:
            raise WrongLogin
        self.db = DatabaseHandler("database.db")

    def book_format_check(self, book_path):
        book_format = book_path.split(".")[-1]
        if book_format not in self.support_format:
            raise TypeError
        return book_format

    def book_path_check(self, book_path):
        if not book_path:
            raise ValueError

    def add_book(self, book_path):
        self.book_path_check(book_path)
        book_format = self.book_format_check(book_path)
        file_name = os.path.basename(book_path)
        if book_format == "fb2" or book_format == "epub":
            book = ebookmeta.get_metadata(book_path)
            if self.db.get_book_id(self.db.get_user_id(self.user_login), book.title):
                raise BookExists
            self.db.add_book(
                self.db.get_user_id(self.user_login),
                book.title,
                book.get_author_string(),
                book.description,
                book.get_tag_string(),
                book.lang,
                f"UserBooks/{self.user_login}/{file_name}"
            )
        shutil.copy(book_path, f"UserBooks/{self.user_login}")

    def del_book(self, book_path):
        self.db.del_book(book_path)
        os.remove(book_path)
        return True

    def open_reader(self, book_path):
        os.startfile(os.path.abspath(book_path), "open")
