import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow

import CustomExceptions as Ce
from BookHandler import BookHandler
from DatabaseHandler import DatabaseHandler


class LoginUI(QDialog):  # Окно входа в свой аккаунт с библиотекой
    def __init__(self, database):
        super().__init__()
        self.login = ""
        self.db = database
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/login.ui", self)  # Загружаем дизайн
        self.buttonBox.accepted.connect(self.check_login)
        self.buttonBox.rejected.connect(self.form_quit)
        self.reg.clicked.connect(self.open_reg_form)

    def check_login(self):
        login = self.login_text.text()
        password = self.pass_text.text()
        res = False
        try:
            res = self.db.check_login(login, password)
        except Ce.WrongLoginError:
            self.status.setText("Неправильный логин")
        except Ce.WrongPasswordError:
            self.status.setText("Неправильный пароль")
        if res:
            self.login = login
            self.accept()

    def get_login(self):
        return self.login

    def form_quit(self):
        self.reject()

    def open_reg_form(self):
        self.reg_form = RegistrationUI(self.db)
        self.reg_form.show()


class RegistrationUI(QDialog):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/register.ui", self)  # Загружаем дизайн
        self.buttonBox.accepted.connect(self.register)
        self.buttonBox.rejected.connect(self.form_quit)

    def register(self):
        login = self.login_text.text()
        password = self.pass_text.text()
        res = False
        try:
            res = self.db.register(login, password)
        except Ce.UserExistsError:
            self.status.setText("Такой логин уже существует")
        except Ce.WrongLoginError:
            self.status.setText("Неправильный логин или пароль")
        except Ce.ShortLoginError:
            self.status.setText("Логин меньше 4-х символов")
        if res:
            self.accept()

    def form_quit(self):
        self.reject()


class CreateTagUI(QDialog):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/createTag.ui", self)  # Загружаем дизайн
        self.error_dialog = QtWidgets.QErrorMessage()
        self.buttonBox.accepted.connect(self.create_tag)
        self.buttonBox.rejected.connect(self.form_quit)

    def form_quit(self):
        self.reject()

    def take_tag_name(self):
        name = self.name_text.text()
        if name == "":
            raise Ce.WrongTagError
        if self.db.check_tag(name):
            raise Ce.TagExistsError
        return name

    def create_tag(self):
        res = False
        try:
            self.tag = self.take_tag_name()
            res = self.db.create_tag(self.tag)
        except Ce.WrongTagError:
            self.error_dialog.showMessage("Неправильная метка")
            self.error_dialog.exec_()
        except Ce.TagExistsError:
            self.error_dialog.showMessage("Tакая метка уже есть")
            self.error_dialog.exec_()
        if res:
            self.accept()


class RemoveTagUI(QDialog):
    def __init__(self, database, login, books):
        super().__init__()
        self.db = database
        self.login = login
        self.books_list = self.clean_book_list(books)
        self.initUI()

    def clean_book_list(self, bookslist):
        res = []
        if self.login and bookslist:
            for i in bookslist:
                if self.db.get_book_tags(self.login, i):
                    res.append(i)
        return res

    def initUI(self):
        uic.loadUi("UI/readBookForm.ui", self)  # Загружаем дизайн
        self.window().setWindowTitle("Отвязка метки")
        self.BookChose.addItems(self.books_list)
        self.buttonBox.accepted.connect(self.open_two_form)
        self.buttonBox.rejected.connect(self.form_quit)

    def check_books(self, books):
        if not books:
            raise Ce.EmptyLibraryError
        else:
            self.books_list = self.clean_book_list(books)

    def initChoseTagForm(self, login, user_id, book):
        self.chose_tag_form = RemoveTagChoseTagUI(self.db, login, user_id, book)
        self.chose_tag_form.accepted.connect(self.accept_close_form)

    def form_quit(self):
        self.reject()

    def open_two_form(self):
        user_id = self.db.get_user_id(self.login)
        book = self.BookChose.currentText()
        self.initChoseTagForm(self.login, user_id, book)
        self.chose_tag_form.show()

    def accept_close_form(self):
        self.clean_book_list(self.books_list)
        self.accept()


class RemoveTagChoseTagUI(QDialog):
    def __init__(self, database, login, user_id, book):
        super().__init__()
        self.db = database
        self.login = login
        self.user_id = user_id
        self.book = book
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/readTagForm.ui", self)  # Загружаем дизайн
        self.window().setWindowTitle("Отвязка метки")
        self.tag.addItems(self.db.get_book_tags(self.login, self.book))
        self.buttonBox.accepted.connect(self.remove_tag)
        self.buttonBox.rejected.connect(self.form_quit)

    def form_quit(self):
        self.reject()

    def remove_tag(self):
        chose_tag = self.tag.currentText()
        self.db.remove_tag(self.db.get_book_id(self.user_id, self.book), chose_tag)
        self.accept()


class LinkTagUI(QDialog):
    def __init__(self, database, login, books):
        super().__init__()
        self.db = database
        self.login = login
        self.books_list = books
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/readBookForm.ui", self)  # Загружаем дизайн
        self.window().setWindowTitle("Привязка метки")
        self.BookChose.addItems(self.books_list)
        self.buttonBox.accepted.connect(self.open_two_form)
        self.buttonBox.rejected.connect(self.form_quit)

    def initChoseTagForm(self, login, user_id, book):
        self.chose_tag_form = LinkTagChoseTag(self.db, login, user_id, book)
        self.chose_tag_form.accepted.connect(self.accept_close_form)

    def form_quit(self):
        self.reject()

    def check_books(self, books):
        if not books:
            raise Ce.EmptyLibraryError

    def open_two_form(self):
        user_id = self.db.get_user_id(self.login)
        book = self.BookChose.currentText()
        self.initChoseTagForm(self.login, user_id, book)
        self.chose_tag_form.show()

    def accept_close_form(self):
        self.accept()


class LinkTagChoseTag(QDialog):
    def __init__(self, database, login, user_id, book):
        super().__init__()
        self.db = database
        self.login = login
        self.user_id = user_id
        self.book = book
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/readTagForm.ui", self)  # Загружаем дизайн
        self.window().setWindowTitle("Привязка метки")
        self.tag.addItems(self.clean_tag_list())
        self.buttonBox.accepted.connect(self.link_tag)
        self.buttonBox.rejected.connect(self.form_quit)

    def clean_tag_list(self):
        res = []
        if self.login and self.book:
            tags = self.db.get_tags()
            for i in tags:
                if self.db.get_tag_value(self.login, self.book, i) == 1:
                    pass
                else:
                    res.append(i)
        return res

    def form_quit(self):
        self.reject()

    def link_tag(self):
        chose_tag = self.tag.currentText()
        self.db.link_tag(self.login, self.book, chose_tag)
        self.accept()


class DeleteBookUI(QDialog):
    def __init__(self, database, login, books):
        super().__init__()
        self.db = database
        self.book_list = books
        self.login = login
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/deleteBook.ui", self)  # Загружаем дизайн
        self.books.addItems(self.book_list)
        self.buttonBox.accepted.connect(self.delete_book)
        self.buttonBox.rejected.connect(self.form_quit)

    def form_quit(self):
        self.reject()

    def check_books(self, books):
        if not books:
            raise Ce.EmptyLibraryError

    def delete_book(self):
        res = False
        book_h = BookHandler(self.login)
        user_id = self.db.get_user_id(self.login)
        self.book = self.books.currentText()
        self.path = self.db.get_book_path(user_id, self.book)
        res = book_h.del_book(self.path)
        if res:
            self.accept()


class SortBooksUI(QDialog):
    def __init__(self, database, login):
        super().__init__()
        self.db = database
        self.login = login
        self.chose_tag = ""
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/readTagForm.ui", self)  # Загружаем дизайн
        self.window().setWindowTitle("Сортировка")
        self.tag.addItems(self.db.get_tags())
        self.buttonBox.accepted.connect(self.sorting)
        self.buttonBox.rejected.connect(self.form_quit)

    def form_quit(self):
        self.reject()

    def check_books(self, books):
        if not books:
            raise Ce.EmptyLibraryError

    def sorting(self):
        self.chose_tag = self.tag.currentText()
        self.accept()

    def get_tag(self):
        return self.chose_tag


class OpenReaderUI(QDialog):
    def __init__(self, database, login, books):
        super().__init__()
        self.db = database
        self.login = login
        self.books = books
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/readBookForm.ui", self)  # Загружаем дизайн
        self.window().setWindowTitle("Открытие файла для чтения")
        self.BookChose.addItems(self.books)
        self.buttonBox.accepted.connect(self.open_file)
        self.buttonBox.rejected.connect(self.form_quit)

    def form_quit(self):
        self.reject()

    def check_books(self, books):
        if not books:
            raise Ce.EmptyLibraryError

    def open_file(self):
        self.book = self.BookChose.currentText()
        self.book_h = BookHandler(self.login)
        user_id = self.db.get_user_id(self.login)
        self.book_h.open_reader(self.db.get_book_path(user_id, self.book))
        self.accept()


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler("database.db")
        self.user_login = ""
        self.initUI()

    def initUI(self):
        uic.loadUi("UI/main.ui", self)  # Загружаем дизайн
        self.error_dialog = QtWidgets.QErrorMessage()
        self.add_tag_form = CreateTagUI(self.db)
        self.initLoginUI()
        self.initDeleteBookUI(self.user_login, [])
        self.initRemoveTagUI(self.user_login, [])
        self.initLinkTagUI(self.user_login, [])
        self.initSortBooksUI(self.user_login)
        self.initOpenReaderUI(self.user_login, [])

        self.AddBook.clicked.connect(self.add_book)
        self.AddTag.clicked.connect(self.add_tag)
        self.Refresh.clicked.connect(self.refresh)

    def initLoginUI(self):
        self.login_form = LoginUI(self.db)
        self.Login.clicked.connect(self.open_login_form)
        self.login_form.accepted.connect(self.update_booklist)

    def initDeleteBookUI(self, user, books):
        self.delete_book_form = DeleteBookUI(self.db, user, books)
        self.RemoveBook.clicked.connect(self.delete_book)
        self.delete_book_form.accepted.connect(self.update_booklist)

    def initRemoveTagUI(self, login, books):
        self.remove_tag_form = RemoveTagUI(self.db, login, books)
        self.RemoveTag.clicked.connect(self.remove_tag)
        self.remove_tag_form.accepted.connect(self.update_booklist)

    def initLinkTagUI(self, login, books):
        self.link_tag_form = LinkTagUI(self.db, login, books)
        self.LinkTag.clicked.connect(self.link_tag)
        self.link_tag_form.accepted.connect(self.update_booklist)

    def initSortBooksUI(self, login):
        self.sort_book_form = SortBooksUI(self.db, login)
        self.SortBook.clicked.connect(self.sort_book)
        self.sort_book_form.accepted.connect(self.update_booklist_sort)

    def initOpenReaderUI(self, login, books):
        self.open_book_form = OpenReaderUI(self.db, login, books)
        self.ReadBook.clicked.connect(self.open_book)

    def raise_error_dialog(self, msg):
        self.error_dialog.showMessage(msg)
        self.error_dialog.exec_()

    def add_book(self):
        try:
            book_path = QFileDialog.getOpenFileName(
                self, "Выбрать книгу", "", "fb2 (*.fb2);;epub (*.epub);;Все файлы (*)"
            )[0]
            if book_path == "":
                raise ValueError
            book = BookHandler(self.get_username())
            book.add_book(book_path)
            self.update_booklist()
        except ValueError:
            pass
        except Ce.WrongLoginError:
            self.raise_error_dialog("Вы не вошли в аккаунт!")
        except Ce.BookExistsError:
            self.raise_error_dialog("В вашей библиотеке есть данная книга!")
        except TypeError:
            self.raise_error_dialog("Формат не поддерживается!")

    def delete_book(self):
        try:
            login, books = self.check_login_and_get_books()
            if self.get_username() != self.delete_book_form.login:
                self.initDeleteBookUI(login, books)
            self.delete_book_form.check_books(books)
            self.delete_book_form.show()
        except Ce.WrongLoginError:
            self.raise_error_dialog("Вы не вошли в аккаунт!")
        except Ce.EmptyLibraryError:
            self.raise_error_dialog("У вас нет книг!")

    def add_tag(self):
        if self.get_username() == "":
            self.raise_error_dialog("Вы не вошли в аккаунт!")
        else:
            self.add_tag_form.show()

    def remove_tag(self):
        try:
            login, books = self.check_login_and_get_books()
            if self.get_username() != self.remove_tag_form.login:
                self.initRemoveTagUI(login, books)
            self.remove_tag_form.check_books(books)
            self.remove_tag_form.show()
        except Ce.WrongLoginError:
            self.raise_error_dialog("Вы не вошли в аккаунт!")
        except Ce.EmptyLibraryError:
            self.raise_error_dialog("У вас нет книг!")

    def link_tag(self):
        try:
            login, books = self.check_login_and_get_books()
            if self.get_username() != self.link_tag_form.login:
                self.initLinkTagUI(login, books)
            self.link_tag_form.check_books(books)
            self.link_tag_form.show()
        except Ce.WrongLoginError:
            self.raise_error_dialog("Вы не вошли в аккаунт!")
        except Ce.EmptyLibraryError:
            self.raise_error_dialog("У вас нет книг!")

    def sort_book(self):
        try:
            login, books = self.check_login_and_get_books()
            if self.get_username() != self.sort_book_form.login:
                self.initSortBooksUI(login)
            self.sort_book_form.check_books(books)
            self.sort_book_form.show()
        except Ce.WrongLoginError:
            self.raise_error_dialog("Вы не вошли в аккаунт!")
        except Ce.EmptyLibraryError:
            self.raise_error_dialog("У вас нет книг!")

    def open_login_form(self):
        self.login_form.login_text.setText("")
        self.login_form.pass_text.setText("")
        self.login_form.show()

    def refresh(self):
        try:
            self.check_login_and_get_books()
            self.update_booklist()
        except Ce.WrongLoginError:
            self.raise_error_dialog("Вы не вошли в аккаунт!")

    def open_book(self):
        try:
            login, books = self.check_login_and_get_books()
            if self.get_username() != self.open_book_form.login:
                self.initOpenReaderUI(login, books)
            self.open_book_form.check_books(books)
            self.open_book_form.show()
        except Ce.WrongLoginError:
            self.raise_error_dialog("Вы не вошли в аккаунт!")
        except Ce.EmptyLibraryError:
            self.raise_error_dialog("У вас нет книг!")

    def check_login_and_get_books(self):
        login = self.get_username()
        if not login:
            raise Ce.WrongLoginError
        books = self.db.get_user_books(login)
        return login, books

    def get_username(self):
        if self.login_form.get_login() != "":
            self.user_login = self.login_form.get_login()
        return self.user_login

    def update_booklist_sort(self):
        if self.sort_book_form.get_tag() == "":
            pass
        model = QSqlQueryModel()
        model.setQuery(
            f"""SELECT bookName, Author, tag, lang FROM books WHERE
                           userID == {self.db.get_user_id(self.get_username())} AND
                           bookID in (SELECT bookID FROM tags WHERE {self.sort_book_form.get_tag()} == 1)"""
        )
        self.BookList.setModel(model)

    def update_booklist(self):
        model = QSqlQueryModel()
        model.setQuery(
            f"""SELECT bookName, Author, tag, lang FROM books WHERE userID ==
                            {self.db.get_user_id(self.get_username())}"""
        )
        self.BookList.setModel(model)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    sys.exit(app.exec_())
