import sqlite3
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QWidget

from BookHandler import BookHandler
from DatabaseHandler import DatabaseHandler
from CustomExceptions import UserExists, WrongPassword, WrongLogin, ShortLogin


class LoginUI(QDialog):  # Окно входа в свой аккаунт с библиотекой
    def __init__(self, parent):
        super().__init__()
        self.login = ''
        self.db = DatabaseHandler('database.db')
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
            self.close()

    def get_login(self):
        return self.login

    def form_quit(self):
        self.close()

    def open_reg_form(self):
        self.reg_form = RegistrationUI(self)
        self.reg_form.show()


class RegistrationUI(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.db = DatabaseHandler('database.db')
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
            self.close()

    def form_quit(self):
        self.close()


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/main.ui', self)  # Загружаем дизайн
        self.user_login = ''
        self.AddBook.clicked.connect(self.add_book)
        self.Login.clicked.connect(self.open_login_form)

    def add_book(self):
        try:
            book = QFileDialog.getOpenFileName(
                self, 'Выбрать книгу', '',
                'fb2 (*.fb2);;epub (*.epub);;Все файлы (*)')[0]
            book = BookHandler(book)
        except TypeError as e:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Формат не поддерживается!')
            error_dialog.exec_()
        except:
            pass

    def open_login_form(self):
        self.login_form = LoginUI(self)
        self.login_form.show()
        self.user_login = self.login_form.get_login()
        self.auth.setText(f'Пользователь: {self.user_login}')

    def get_username(self, username):
        self.user_login = username


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    sys.exit(app.exec_())
