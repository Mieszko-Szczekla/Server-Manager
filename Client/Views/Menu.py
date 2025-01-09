from PySide6 import QtCore, QtWidgets
from Views.HostnameSetPrompt import HostnameSetPrompt
from Views.UsersManager import UsersManager
from Views.SoftwareManager import SoftwareManager
from Views.FileExplorer import FileExplorer

class Menu(QtWidgets.QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle(f'Connection with {self.app.rm.hostname}')
        self.setFixedSize(250, 200)

        self.software_button = QtWidgets.QPushButton('Software')
        self.explore_button = QtWidgets.QPushButton('Explore files')
        self.user_button = QtWidgets.QPushButton('Manage users')
        self.hostname_button = QtWidgets.QPushButton('Change hostname')

        self.software_button.clicked.connect(self.open_software_cfg)
        self.explore_button.clicked.connect(self.open_explorer)
        self.user_button.clicked.connect(self.open_users_cfg)
        self.hostname_button.clicked.connect(self.open_hostname_cfg)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.software_button)
        self.layout.addWidget(self.explore_button)
        self.layout.addWidget(self.user_button)
        self.layout.addWidget(self.hostname_button)

    @QtCore.Slot()
    def open_software_cfg(self):
        self.software_cfg = SoftwareManager(self.app)

    @QtCore.Slot()
    def open_users_cfg(self):
        self.users_cfg = UsersManager(self.app)

    @QtCore.Slot()
    def open_hostname_cfg(self):
        self.hostname_cfg = HostnameSetPrompt(self.app)

    @QtCore.Slot()
    def open_explorer(self):
        self.explorer = FileExplorer(self.app)



        


