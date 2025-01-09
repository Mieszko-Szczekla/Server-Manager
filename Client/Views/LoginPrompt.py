from PySide6 import QtCore, QtWidgets
from Client import RemoteMachine
import configparser

class LoginPrompt(QtWidgets.QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle('Login Prompt')
        self.setFixedSize(400, 200)
        self.app = app

        self.hostname_label = QtWidgets.QLabel('Hostname  ')
        self.hostname_input = QtWidgets.QLineEdit()
        self.port_label = QtWidgets.QLabel('Port')
        self.port_input = QtWidgets.QLineEdit()
        self.password_label = QtWidgets.QLabel('Password')
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_button = QtWidgets.QPushButton('Confirm')
        self.confirm_button.clicked.connect(self.confirm_login)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.hostname_label, 0, 0)
        self.layout.addWidget(self.hostname_input, 0, 1)
        self.layout.addWidget(self.port_label, 1, 0)
        self.layout.addWidget(self.port_input, 1, 1)
        self.layout.addWidget(self.password_label, 2, 0)
        self.layout.addWidget(self.password_input, 2, 1)
        self.layout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding), 3, 0)
        self.layout.addWidget(self.confirm_button, 4, 0, 1, 2)

        self.parse_config()

        self.show()

    @QtCore.Slot()
    def confirm_login(self):
        rm = RemoteMachine(self.hostname_input.text(), self.port_input.text(), self.password_input.text())
        if rm.ping():
            self.hide()
            self.app.show_menu(rm)
        else:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Could not connect. Verify that all provided info is valid.')

    def parse_config(self):
        config_parser = configparser.RawConfigParser()
        config_path = './config.txt'
        config_parser.read(config_path)
        if 'CLIENT' not in config_parser:
            return
        if 'Host' in config_parser['CLIENT']:
            self.hostname_input.setText(config_parser['CLIENT']['Host'])
        if 'PortNumber' in config_parser['CLIENT'] :
            self.port_input.setText(config_parser['CLIENT']['PortNumber'])
        if 'Password' in config_parser['CLIENT']:
            self.password_input.setText(config_parser['CLIENT']['Password'])
    


