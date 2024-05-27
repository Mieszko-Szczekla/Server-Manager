from PySide6 import QtCore, QtWidgets
import re

REGEX_VALID_USERNAME = re.compile(r'^([a-z_][a-z0-9_]{0,30})$')

def is_valid(username):
    return REGEX_VALID_USERNAME.match(username) is not None

class UsersManager(QtWidgets.QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle('Manage users')
        self.resize(400, 500)
        self.setMinimumSize(350, 200)
        self.app = app

        self.users_list = QtWidgets.QListWidget()
        self.users_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.users_list.itemSelectionChanged.connect(self.update_remove_button)
        self.add_button = QtWidgets.QPushButton('Add')
        self.remove_button = QtWidgets.QPushButton('Remove')
        self.remove_button.setDisabled(True)
        self.password_button = QtWidgets.QPushButton('Change password')
        self.password_button.setDisabled(True)


        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)
        self.button_layout.addWidget(self.password_button)

        self.add_button.clicked.connect(self.add_user)
        self.remove_button.clicked.connect(self.remove_user)
        self.password_button.clicked.connect(self.change_password)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.users_list)
        self.layout.addLayout(self.button_layout)

        self.refresh()
        self.show()

    def refresh(self, update = True):
        if update:
            self.users = self.app.rm.user_list()
        self.users_list.clear()
        for user in self.users:
            self.users_list.addItem(user)

    @QtCore.Slot()
    def add_user(self):
        username, answer = QtWidgets.QInputDialog.getText(self, 'Add user', 'Enter username:')
        if answer:
            if not is_valid(username):
                QtWidgets.QMessageBox.critical(self, 'Error', 'Invalid username!')
            elif username in self.users:
                QtWidgets.QMessageBox.critical(self, 'Error', 'User already exists!')
            elif self.app.rm.user_add(username):
                self.refresh()
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', 'Could not add user. Verify that the username is valid.')

    @QtCore.Slot()
    def remove_user(self):
        selection = self.users_list.currentItem().text()
        if selection != 'root':
            if self.app.rm.user_del(selection):
                self.refresh()
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', 'Could not remove user. Verify that the user exists and is not root.')

    @QtCore.Slot()
    def change_password(self):
        new_password, accepted = QtWidgets.QInputDialog.getText(self, 'Select password', 'Enter new password:')
        selection = self.users_list.currentItem().text()
        if not accepted:
            return
        if new_password != '':
            self.app.rm.passwd(selection, new_password)
        else:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Password can not be empty!')

    @QtCore.Slot()
    def update_remove_button(self):
        if self.users_list.currentItem().text() != 'root':
            self.remove_button.setDisabled(False)
        else:
            self.remove_button.setDisabled(True)
        self.password_button.setDisabled(False)