import sys
import os
import re

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QErrorMessage, QLineEdit, QFileDialog, QMessageBox
from PySide6.QtCore import Qt

sys.path.append(os.path.abspath(''))
from password_db import PasswordDatabase

class FileCreationDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Passtore')
        self.file_path = None
        self.init_dialog()

    def init_dialog(self):
        # define widgets
        self.welcome_label = QLabel('Create a password file:')
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label = QLabel('File Path:')
        self.file_entry = QLineEdit()
        self.file_entry.setEnabled(False)
        self.file_button = QPushButton('...')
        self.file_button.clicked.connect(self.ask_filename)
        self.pass_label = QLabel('Password:')
        self.confirm_label = QLabel('Confirm:')
        self.pass_entry = QLineEdit()
        self.pass_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_entry = QLineEdit()
        self.confirm_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.accept_button = QPushButton('Accept')
        self.accept_button.clicked.connect(self.create_file)
        # this label is only given text if the user provides invalid input
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: #ff0000')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # create the layout for the widget and place all widgets
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.welcome_label, 0, 0, 1, 3)
        self.main_layout.addWidget(self.file_label, 1, 0, 1, 1)
        self.main_layout.addWidget(self.file_entry, 1, 1, 1, 1)
        self.main_layout.addWidget(self.file_button, 1, 2, 1, 1)
        self.main_layout.addWidget(self.pass_label, 2, 0, 1, 1)
        self.main_layout.addWidget(self.pass_entry, 2, 1, 1, 1)
        self.main_layout.addWidget(self.confirm_label, 3, 0, 1, 1)
        self.main_layout.addWidget(self.confirm_entry, 3, 1, 1, 1)
        self.main_layout.addWidget(self.accept_button, 4, 1, 1, 1)
        self.main_layout.addWidget(self.error_label, 5, 0, 1, 3)
        self.setLayout(self.main_layout)

    def ask_filename(self):
        file_path = QFileDialog.getSaveFileName(filter='Password Database Files (*.pwdb)')[0]
        if file_path: 
            self.file_entry.setText(file_path) 
            self.file_path = file_path
            if not self.file_path.endswith('.pwdb'):
                self.file_path += '.pwdb'
        
    def create_file(self):
        # clear the error text if present
        self.error_label.setText('')
        # verify that password and confirmation match
        password = self.pass_entry.text()
        confirmation = self.confirm_entry.text()
        if password != confirmation:
            self.error_label.setText('Password and confirmation do not match')
        # check password length
        if len(password) < 8:
            self.error_label.setText('Password must be at least 8 Characters long')
            return
        # ensure the password contains uppercase letters, lowercase letters, numbers and special charachters 
        for i in (r'[a-z]', r'[A-z]', r'[\d]', r'[!@#$%^&*(),.?\":{}|<>]'):
            if not re.search(i, password):
                print(i)
                QErrorMessage(self).showMessage('Your password must have at least one of each of the following:\nUppercase Letters\nLowercase Letters\nNumbers\nSpecial Characters')
                return 
        # create a password database with the provided password
        try:
            password_database = PasswordDatabase(self.file_path, password)
            password_database.create_file()
            password_database.save_file()
            message_box = QMessageBox(self)
            message_box.setText('The password file was created succesfully')
            message_box.exec()
            self.close()
        except PermissionError:
            self.error_label.setText('Invalid directory')



