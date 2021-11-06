import sqlite3
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QWidget

from BookHandler import BookHandler


class LoginUI(QDialog): # Окно входа в свой аккаунт с библиотекой
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/login.ui', self)  # Загружаем дизайн



class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/main.ui', self)  # Загружаем дизайн
        self.AddBook.clicked.connect(self.add_book)
        self.Login.clicked.connect(self.open_login_form)

    def add_book(self):
        book = QFileDialog.getOpenFileName(
            self, 'Выбрать книгу', '',
            'fb2 (*.fb2);;epub (*.epub);;Все файлы (*)')[0]
        book = BookHandler(book)
        try:
            book = BookHandler(book)
        except TypeError as e:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Формат не поддерживается!')
    def open_login_form(self):
        self.login_form = LoginUI()
        self.login_form.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    sys.exit(app.exec_())