import sys

from BookHandler import BookHandler
from CustomExceptions import UserExists, WrongPassword, WrongLogin, ShortLogin
from DatabaseHandler import DatabaseHandler
from PyQt5 import uic, QtWidgets
from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PyQt5.QtWidgets import QMainWindow


class LoginUI(QDialog):  # Окно входа в свой аккаунт с библиотекой
    def __init__(self):
        super().__init__()
        self.login = ''
        self.db = DatabaseHandler('database.db')
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
        self.reg_form = RegistrationUI(self)
        self.reg_form.show()


class RegistrationUI(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.db = DatabaseHandler('database.db')
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
            self.close()

    def form_quit(self):
        self.close()


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler('database.db')
        self.user_login = ''
        self.initUI()

    def initUI(self):
        uic.loadUi('UI/main.ui', self)  # Загружаем дизайн
        self.login_form = LoginUI()
        self.error_dialog = QtWidgets.QErrorMessage()
        self.AddBook.clicked.connect(self.add_book)
        self.Login.clicked.connect(self.open_login_form)
        self.login_form.accepted.connect(self.update_booklist)

    def add_book(self):
        try:
            book = QFileDialog.getOpenFileName(
                self, 'Выбрать книгу', '',
                'fb2 (*.fb2);;epub (*.epub);;Все файлы (*)')[0]
            book = BookHandler(self.get_username(), book)
        except WrongLogin:
            self.error_dialog.showMessage(f'Вы не вошли в аккаунт!')
            self.error_dialog.exec_()
        except TypeError:
            self.error_dialog.showMessage(f'Формат не поддерживается!')
            self.error_dialog.exec_()
        except:
            pass

    def open_login_form(self):
        self.login_form.show()

    def get_username(self):
        if self.login_form.get_login() != '':
            self.user_login = self.login_form.get_login()
        return self.user_login

    def update_booklist(self):
        model = QSqlQueryModel()
        model.setQuery(f"""SELECT bookName, Author FROM books""")
        self.BookList.setModel(model)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    sys.exit(app.exec_())
