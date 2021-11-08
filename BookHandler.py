import os
import shutil
import ebookmeta
from DatabaseHandler import DatabaseHandler
from CustomExceptions import WrongLogin

class BookHandler:
    def __init__(self, login, book):
        self.support_format = ['fb2', 'epub', 'pdf']
        self.book_path = book
        if login:
            self.user_login = login
        else:
            raise WrongLogin
        self.book_format = self.book_format_check()
        self.db = DatabaseHandler('database.db')

    def book_format_check(self):
        book_format = self.book_path.split('.')[-1]
        if book_format not in self.support_format:
            raise TypeError
        return book_format

    def add_book(self):
        shutil.copy(self.book_path, f'UserBooks/{self.user_login}')
        if self.book_format == 'fb2':
            book = ebookmeta.get_metadata(self.book_path)
            self.db.add_book(
                self.db.get_user_id(self.user_login),
                book.title,
                book.get_author_string(),
                book.description,
                book.get_tag_string(),
                book.lang
            )
        elif self.book_format == 'epub':
            pass
        elif self.book_format == 'pdf':
            pass

tmp = BookHandler("test", "TestBooks\Alisa v Stranie chudies - L'iuis Kerroll.fb2")
tmp.add_book()