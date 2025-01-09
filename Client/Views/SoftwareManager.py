import sys
from PySide6 import QtWidgets, QtCore
from bs4 import BeautifulSoup
from requests import get


def package_search(term):
    querry = 'https://packages.debian.org/search?suite=stable&section=all&arch=any&searchon=names&keywords='+term.replace(' ', '+')
    html = BeautifulSoup(get(querry).text, 'html.parser')
    return list(map(lambda element: element.text[8:], html.select('h3')))

def package_info(package):
    querry = 'https://packages.debian.org/bookworm/'+package
    html = BeautifulSoup(get(querry).text, 'html.parser')
    descriptions = html.select('#pdesc')[0].children
    #print(descriptions)
    next(descriptions)
    title = next(descriptions).text
    next(descriptions)
    description = next(descriptions).text.replace('\n', ' ')
    return {'title': title, 'description': description}

class SoftwareManager(QtWidgets.QWidget):
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle('Manage software')
        self.resize(600, 500)
        self.setMinimumSize(350, 200)
        self.app = app

        self.packages_list = QtWidgets.QListWidget()
        self.packages_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.install_button = QtWidgets.QPushButton('Install')
        self.remove_button = QtWidgets.QPushButton('Remove')
        self.remove_button.setDisabled(True)
        self.install_button.setDisabled(True)
        self.package_title = QtWidgets.QLabel('')
        self.package_description = QtWidgets.QLabel('')
        self.scroll = QtWidgets.QScrollArea()
        self.search_input = QtWidgets.QLineEdit()
        self.package_info_layout = QtWidgets.QVBoxLayout()

        self.left_pane = QtWidgets.QVBoxLayout()
        self.right_pane = QtWidgets.QVBoxLayout()
        self.buttons_layout = QtWidgets.QHBoxLayout()

        self.package_title.setWordWrap(True)
        self.package_description.setWordWrap(True)
        self.package_title.setStyleSheet("font-weight: bold; font-size: 20px")
        self.package_info_layout.addWidget(self.package_title)
        self.package_info_layout.addWidget(self.package_description)
        self.package_info_layout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.scroll.setLayout(self.package_info_layout)
        self.buttons_layout.addWidget(self.install_button)
        self.buttons_layout.addWidget(self.remove_button)

        self.left_pane.addWidget(self.search_input)
        self.left_pane.addWidget(self.packages_list)
        self.right_pane.addWidget(self.scroll)
        self.right_pane.addLayout(self.buttons_layout)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addLayout(self.left_pane)
        self.layout.addLayout(self.right_pane)

        self.search_input.returnPressed.connect(self.search)
        self.packages_list.itemSelectionChanged.connect(self.display_details)
        self.install_button.clicked.connect(self.install)
        self.remove_button.clicked.connect(self.remove)

        #self.refresh()
        self.show()

    @QtCore.Slot()
    def display_details(self):
        answer = package_info(self.packages_list.currentItem().text())
        self.package_title.setText(answer['title'])
        self.package_description.setText(answer['description'])
        self.update_buttons()

    def update_buttons(self):
        if self.app.rm.is_installed(self.packages_list.currentItem().text()):
            self.install_button.setDisabled(True)
            self.remove_button.setDisabled(False)
        else:
            self.install_button.setDisabled(False)
            self.remove_button.setDisabled(True)
        
    @QtCore.Slot()
    def search(self):
        querry = self.search_input.text()
        if querry != '':
            self.packages_list.clear()
            self.install_button.setDisabled(True)
            self.remove_button.setDisabled(True)
            self.package_title.setText('')
            self.package_description.setText('')
            for package in package_search(querry):
                self.packages_list.addItem(package)

    QtCore.Slot()
    def install(self):
        package = self.packages_list.currentItem().text()
        if error_code := self.app.rm.install(package):
            QtWidgets.QMessageBox.critical(self, 'Error', f'Could not install package. Error code: {error_code}.')
        else:
            self.update_buttons()
            
    QtCore.Slot()
    def remove(self):
        package = self.packages_list.currentItem().text()
        if error_code := self.app.rm.purge(package):
            QtWidgets.QMessageBox.critical(self, 'Error', f'Could not remove package. Error code: {error_code}.')
        else:
            self.update_buttons()
            