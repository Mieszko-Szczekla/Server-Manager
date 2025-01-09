import sys
from PySide6 import QtCore, QtWidgets
from Views.LoginPrompt import LoginPrompt
from Views.Menu import Menu

class App:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.login_prompt = LoginPrompt(self)
        self.login_prompt.show()
        sys.exit(self.app.exec())

    def show_menu(self, rm):
        if rm is None:
            sys.exit(-1)
        self.rm = rm
        self.menu = Menu(self)
        self.menu.show()

    def refresh_hostname(self):
        self.menu.setWindowTitle(f'Connection with {self.rm.hostname}')

if __name__ == '__main__':
    App()