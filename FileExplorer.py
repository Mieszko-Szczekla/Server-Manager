from PySide6 import QtCore, QtWidgets
import re
from functools import reduce
from operator import add

REGEX_VALID_USERNAME = re.compile(r'^([a-z_][a-z0-9_]{0,30})$')

def is_valid(username):
    return REGEX_VALID_USERNAME.match(username) is not None

class FileExplorer(QtWidgets.QWidget):
    def __init__(self, app):
        super().__init__()
        self.current_dir_contents = []
    
        self.setWindowTitle('File manager')
        self.resize(600, 500)
        self.setMinimumSize(500, 200)
        self.app = app

        self.files_list = QtWidgets.QListWidget()
        self.files_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.path_bar = QtWidgets.QLineEdit('/')
        self.upload_button = QtWidgets.QPushButton('Upload')
        self.download_button = QtWidgets.QPushButton('Download')
        self.download_button.setDisabled(True)
        self.remove_button = QtWidgets.QPushButton('Remove')
        self.remove_button.setDisabled(True)
        self.up_button = QtWidgets.QPushButton('^')
        self.up_button.setDisabled(True)
        self.properties_label = QtWidgets.QLabel('Properties')
        self.properties_content = QtWidgets.QTextEdit()
        self.properties_content.setReadOnly(True)
        
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.path_ui = QtWidgets.QHBoxLayout()
        self.left_pane = QtWidgets.QVBoxLayout()
        self.right_pane = QtWidgets.QVBoxLayout()

        self.buttons_layout.addWidget(self.upload_button)
        self.buttons_layout.addWidget(self.download_button)
        self.buttons_layout.addWidget(self.remove_button)

        self.path_ui.addWidget(self.up_button)
        self.path_ui.addWidget(self.path_bar)

        self.left_pane.addLayout(self.path_ui)
        self.left_pane.addWidget(self.files_list)

        self.right_pane.addLayout(self.buttons_layout)
        self.right_pane.addWidget(self.properties_label)
        self.right_pane.addWidget(self.properties_content)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addLayout(self.left_pane)
        self.layout.addLayout(self.right_pane)

        self.files_list.itemSelectionChanged.connect(self.update_properties)
        self.path_bar.returnPressed.connect(self.update_files)
        self.files_list.itemDoubleClicked.connect(self.change_directory)
        self.up_button.clicked.connect(self.go_up)
        self.download_button.clicked.connect(self.download)
        self.remove_button.clicked.connect(self.remove)
        self.upload_button.clicked.connect(self.upload)

        self.update_files()

        self.show()

    @QtCore.Slot()
    def change_directory(self):
        selected = self.files_list.currentItem().text()
        items = list(filter(lambda dict: dict['filename'] == selected, self.current_dir_contents))

        if selected != '' and items != []:
            if not items[0]['is_directory']:
                return


        self.path_bar.setText(
            self.path_bar.text() + 
            ('/' if self.path_bar.text()[-1] != '/' else '') + 
            self.files_list.currentItem().text()
        )
        self.update_files()

    QtCore.Slot()
    def update_properties(self):
        self.download_button.setDisabled(True)
        self.remove_button.setDisabled(True)
        self.properties_content.clear()
        selectedItem = self.files_list.currentItem()
        if selectedItem is not None:
            items = list(filter(lambda dict: dict['filename'] == selectedItem.text(), self.current_dir_contents))
            if items == []:
                return
        else:
            return
        
        item = items[0]
        self.properties_content.append('Name: ' + item['filename'])
        self.properties_content.append('Size: ' + str(item['size']))
        self.properties_content.append('Owner: ' + item['user'])
        self.properties_content.append('Permissions: ' + item['permissions'])
        self.properties_content.append('Last modified: ' + item['datetime'].strftime('%m-%d %H:%M:%S') if item['datetime'] is not None else 'Unknown')

        self.remove_button.setDisabled(False)
        if not item['is_directory']:
            self.download_button.setDisabled(False)

    @QtCore.Slot()
    def update_files(self):
        path = self.path_bar.text()
        self.current_dir_contents = self.app.rm.ls(path)
        if self.current_dir_contents is None:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Invalid path')
            self.path_bar.setText('/')
            self.update_files()
            return
        self.files_list.clear()
        self.download_button.setDisabled(True)
        self.remove_button.setDisabled(True)
        for file in self.current_dir_contents:
            self.files_list.addItem(file['filename'])
        if path == '/':
            self.up_button.setDisabled(True)
        else:
            self.up_button.setDisabled(False)
        self.properties_content.clear()

    @QtCore.Slot()
    def go_up(self):
        path = self.path_bar.text()
        while(path != '' and path[-1] == '/'):
            path = path[:-1]
        dirs = filter(lambda x: x != '', path.split('/'))
        dirs = list(map(lambda x: '/' + x, dirs))
        if len(dirs) > 1:
            self.path_bar.setText(reduce(add, dirs[:-1], ''))
        else:
            self.path_bar.setText('/')
        self.update_files()
        
    def get_selected_file_path(self):
        selected = self.files_list.currentItem()
        if selected is None:
            return None
        return self.path_bar.text() + '/' + selected.text()
    
    @QtCore.Slot()
    def download(self):
        path = self.get_selected_file_path()
        if path is None:
            return
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', path)
        if save_path == '':
            return
        self.app.rm.pull(path, save_path)

    @QtCore.Slot()
    def remove(self):
        path = self.get_selected_file_path()
        if path is None:
            return
        self.app.rm.rm(path)
        self.update_files()

    @QtCore.Slot()
    def upload(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Upload file')
        if path == '':
            return
        self.app.rm.push(path, self.path_bar.text() + '/' + path.split('/')[-1])
        self.update_files()