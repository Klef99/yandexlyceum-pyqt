import sqlite3
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QWidget

from BookHandler import BookHandler
from DatabaseHandler import DatabaseHandler


class LoginUI(QDialog):  # Окно входа в свой аккаунт с библиотекой
    def __init__(self, parent):
        super().__init__()
        self.db = DatabaseHandler('database.db')
        uic.loadUi('UI/login.ui', self)  # Загружаем дизайн
        self.buttonBox.accepted.connect(self.check_login)
        self.buttonBox.rejected.connect(self.form_quit)
        self.reg.clicked.connect(self.open_reg_form)

    def check_login(self):
        login = login_text.text()
        password = pass_text.text()
        if self.db.check_login(login, password):
            parent.get_username(login)
            self.close()

    def form_quit(self):
        self.close()

    def open_reg_form(self):
        pass


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
            error_dialog.show()
        except:
            pass

    def open_login_form(self):
        self.login_form = LoginUI(self)
        self.login_form.show()

    def get_username(self, username):
        self.user_login = username


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    sys.exit(app.exec_())
