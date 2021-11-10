import sys

from BookHandler import BookHandler
from CustomExceptions import *
from DatabaseHandler import DatabaseHandler
from PyQt5 import uic, QtWidgets
from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PyQt5.QtWidgets import QMainWindow


class LoginUI(QDialog):  # Окно входа в свой аккаунт с библиотекой
    def __init__(self, database):
        super().__init__()
        self.login = ''
        self.db = database
        self.initUI()

    def initUI(self):
        uic.loadUi('UI/login.ui', self)  # Загружаем дизайн
        self.buttonBox.accepted.connect(self.check_login)
        self.buttonBox.rejected.connect(self.form_quit)
        self.reg.clicked.connect(self.open_reg_form)

    def check_login(self):
        login = self.login_text.text()
        password = self.pass_text.text()
        res = False
        try:
            res = self.db.check_login(login, password)
        except WrongLogin:
            self.status.setText('Неправильный логин')
        except WrongPassword:
            self.status.setText('Неправильный пароль')
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
        uic.loadUi('UI/register.ui', self)  # Загружаем дизайн
        self.buttonBox.accepted.connect(self.register)
        self.buttonBox.rejected.connect(self.form_quit)

    def register(self):
        login = self.login_text.text()
        password = self.pass_text.text()
        res = False
        try:
            res = self.db.register(login, password)
        except UserExists:
            self.status.setText('Такой логин уже существует')
        except WrongLogin:
            self.status.setText('Неправильный логин или пароль')
        except ShortLogin:
            self.status.setText('Логин меньше 4-х символов')
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
        uic.loadUi('UI/createTag.ui', self)  # Загружаем дизайн
        self.error_dialog = QtWidgets.QErrorMessage()
        self.buttonBox.accepted.connect(self.create_tag)
        self.buttonBox.rejected.connect(self.form_quit)

    def form_quit(self):
        self.reject()

    def take_tag_name(self):
        name = self.name_text.text()
        if name == '':
            raise WrongTag
        if self.db.check_tag(name):
            raise TagExists
        return name

    def create_tag(self):
        res = False
        try:
            self.tag = self.take_tag_name()
            res = self.db.create_tag(self.tag)
        except WrongTag:
            self.error_dialog.showMessage('Неправильная метка')
            self.error_dialog.exec_()
        except TagExists:
            self.error_dialog.showMessage('Tакая метка уже есть')
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
        if self.login and bookslist:
            for i in bookslist:
                if self.db.get_book_tags(self.login, i) == '':
                    del bookslist[bookslist.index(i)]
        return bookslist

    def initUI(self):
        uic.loadUi('UI/deleteLinkTag.ui', self)  # Загружаем дизайн
        self.BookChose.addItems(self.books_list)
        self.buttonBox.accepted.connect(self.open_two_form)
        self.buttonBox.rejected.connect(self.form_quit)

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
        uic.loadUi('UI/deleteLinkTag2.ui', self)  # Загружаем дизайн
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
        uic.loadUi('UI/deleteLinkTag.ui', self)  # Загружаем дизайн
        self.window().setWindowTitle("Привязка метки")
        self.BookChose.addItems(self.books_list)
        self.buttonBox.accepted.connect(self.open_two_form)
        self.buttonBox.rejected.connect(self.form_quit)

    def initChoseTagForm(self, login, user_id, book):
        self.chose_tag_form = LinkTagChoseTag(self.db, login, user_id, book)
        self.chose_tag_form.accepted.connect(self.accept_close_form)

    def form_quit(self):
        self.reject()

    def open_two_form(self):
        user_id = self.db.get_user_id(self.login)
        book = self.BookChose.currentText()
        self.initChoseBookForm(self.login, user_id, book)
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
        uic.loadUi('UI/deleteLinkTag2.ui', self)  # Загружаем дизайн
        self.tag.addItems(self.db.get_book_tags(self.login, self.book))
        self.buttonBox.accepted.connect(self.remove_tag)
        self.buttonBox.rejected.connect(self.form_quit)

    def form_quit(self):
        self.reject()

    def remove_tag(self):
        chose_tag = self.tag.currentText()
        self.db.remove_tag(self.db.get_book_id(self.user_id, self.book), chose_tag)
        self.accept()


class DeleteBookUI(QDialog):
    def __init__(self, database, login, books):
        super().__init__()
        self.db = database
        self.book_list = books
        self.login = login
        self.initUI()

    def initUI(self):
        uic.loadUi('UI/deleteBook.ui', self)  # Загружаем дизайн
        self.books.addItems(self.book_list)
        self.buttonBox.accepted.connect(self.delete_book)
        self.buttonBox.rejected.connect(self.form_quit)

    def form_quit(self):
        self.reject()

    def delete_book(self):
        res = False
        book_h = BookHandler(self.login)
        user_id = self.db.get_user_id(self.login)
        self.book = self.books.currentText()
        self.path = self.db.get_book_path(user_id, self.book)
        res = book_h.del_book(self.path)
        if res:
            self.accept()


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler('database.db')
        self.user_login = ''
        self.initUI()

    def initUI(self):
        uic.loadUi('UI/main.ui', self)  # Загружаем дизайн
        self.login_form = LoginUI(self.db)
        self.error_dialog = QtWidgets.QErrorMessage()
        self.initDeleteBookUI(self.user_login, [])
        self.initRemoveTagUI(self.user_login, [])
        self.Login.clicked.connect(self.open_login_form)
        self.AddBook.clicked.connect(self.add_book)
        self.AddTag.clicked.connect(self.add_tag)
        self.login_form.accepted.connect(self.update_booklist)

    def initDeleteBookUI(self, user, books):
        self.delete_book_form = DeleteBookUI(self.db, user, books)
        self.RemoveBook.clicked.connect(self.delete_book)
        self.delete_book_form.accepted.connect(self.update_booklist)

    def initRemoveTagUI(self, login, books):
        self.remove_tag_form = RemoveTagUI(self.db, login, books)
        self.RemoveTag.clicked.connect(self.remove_tag)
        self.remove_tag_form.accepted.connect(self.update_booklist)

    def raise_error_dialog(self, msg):
        self.error_dialog.showMessage(msg)
        self.error_dialog.exec_()

    def add_book(self):
        try:
            book_path = QFileDialog.getOpenFileName(
                self, 'Выбрать книгу', '',
                'fb2 (*.fb2);;epub (*.epub);;Все файлы (*)')[0]
            if book_path == '':
                raise ValueError
            book = BookHandler(self.get_username())
            book.add_book(book_path)
            self.update_booklist()
        except ValueError:
            pass
        except WrongLogin:
            self.raise_error_dialog('Вы не вошли в аккаунт!')
        except BookExists:
            self.raise_error_dialog('В вашей библиотеке есть данная книга')
        except TypeError:
            self.raise_error_dialog('Формат не поддерживается!')

    def delete_book(self):
        try:
            login = self.get_username()
            if not login:
                raise WrongLogin
            books = self.db.get_user_books(login)
            self.initDeleteBookUI(login, books)
            self.delete_book_form.show()
        except WrongLogin:
            self.raise_error_dialog('Вы не вошли в аккаунт!')

    def add_tag(self):
        self.AddTag_form = CreateTagUI(self.db)
        if self.get_username() == '':
            self.raise_error_dialog('Вы не вошли в аккаунт!')
        else:
            self.AddTag_form.show()

    def remove_tag(self):
        try:
            login = self.get_username()
            if not login:
                raise WrongLogin
            books = self.db.get_user_books(login)
            self.initRemoveTagUI(login, books)
            self.remove_tag_form.show()
        except WrongLogin:
            self.raise_error_dialog('Вы не вошли в аккаунт!')

    def open_login_form(self):
        self.login_form.show()

    def get_username(self):
        if self.login_form.get_login() != '':
            self.user_login = self.login_form.get_login()
        return self.user_login

    def update_booklist(self):
        model = QSqlQueryModel()
        model.setQuery(f"""SELECT bookName, Author, tag, lang FROM books WHERE userID ==
                            {self.db.get_user_id(self.get_username())}""")
        self.BookList.setModel(model)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    sys.exit(app.exec_())
