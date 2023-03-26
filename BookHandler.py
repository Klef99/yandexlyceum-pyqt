import os
import shutil
from pathlib import Path

import ebookmeta

import CustomExceptions as Ce
from DatabaseHandler import DatabaseHandler


class BookHandler:
    def __init__(self, login: str) -> None:
        self.support_format = ["fb2", "epub"]
        if login:
            self.user_login = login
        else:
            raise Ce.WrongLoginError
        self.db = DatabaseHandler("database.db")

    def _book_format_check(self, book_path: Path) -> str:
        book_format = book_path.suffix[1:]
        if book_format not in self.support_format:
            raise TypeError
        return book_format

    def add_book(self, book_path: str) -> None:
        path = Path(book_path)
        if not path.exists():
            raise ValueError
        book_format = self._book_format_check(path)
        file_name = path.name
        if book_format == "fb2" or book_format == "epub":
            book = ebookmeta.get_metadata(book_path)
            if self.db.get_book_id(self.db.get_user_id(self.user_login), book.title):
                raise Ce.BookExistsError
            self.db.add_book(
                self.db.get_user_id(self.user_login),
                book.title,
                book.get_author_string(),
                book.description,
                book.get_tag_string(),
                book.lang,
                f"UserBooks/{self.user_login}/{file_name}",
            )
        shutil.copy(book_path, f"UserBooks/{self.user_login}")

    def del_book(self, book_path: str) -> bool:
        path = Path(book_path)
        self.db.del_book(book_path)
        path.unlink()
        return True

    def open_reader(self, book_path: str) -> None:
        path = Path(book_path)
        os.startfile(path.resolve(), "open")
