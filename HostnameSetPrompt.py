from PySide6 import QtCore, QtWidgets
from ClientTest import RemoteMachine
import re

REGEX_VALID_HOSTNAME = re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])$')


def is_valid(hostname): # TODO implement check
    return REGEX_VALID_HOSTNAME.match(hostname) is not None

class HostnameSetPrompt(QtWidgets.QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle('Change hostname')
        self.setFixedSize(400, 120)

        self.hostname_info = QtWidgets.QLabel(f'Hostname is "{self.app.rm.hostname}".')
        self.hostname_label = QtWidgets.QLabel('New hostname:')
        self.hostname_input = QtWidgets.QLineEdit()
        self.confirm_button = QtWidgets.QPushButton('Confirm')
        self.hostname_layout = QtWidgets.QHBoxLayout()
        self.hostname_layout.addWidget(self.hostname_label)
        self.hostname_layout.addWidget(self.hostname_input)

        self.confirm_button.clicked.connect(self.confirm_change)
        self.hostname_input.returnPressed.connect(self.confirm_change)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.hostname_info)
        self.layout.addLayout(self.hostname_layout)
        self.layout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.layout.addWidget(self.confirm_button)

        self.show()

    @QtCore.Slot()
    def confirm_change(self):
        hostname = self.hostname_input.text()
        if is_valid(hostname):
            self.app.rm.hostname = hostname
            self.hide()
            self.app.refresh_hostname()
        else:
            QtWidgets.QMessageBox.warning(self, 'Invalid hostname', 'Invalid hostname. Please use only letters, numbers and hyphens.')



    


