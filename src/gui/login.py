import sys
import os

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QErrorMessage, QLineEdit, QFileDialog, QApplication
from PySide6.QtCore import Qt

sys.path.append(os.path.abspath('src'))
from password_db import PasswordDatabase

# a window to take master password and attempt to initalize a given password file with it
class LoginWindow(QWidget):
    def __init__(self, file_path: str):
            super().__init__()
            self.file_path = file_path
            self.enter = QShortcut(QKeySequence('Return'), self)
            self.enter.activated.connect(self.decrypt_passwords)
            self.init_dialog()

    def init_dialog(self):
        self.setWindowTitle(f'Unlock {os.path.basename(self.file_path)}')
        self.attempts = 0 # keep track of the number of times the user has attepted to decrypt the password file
        self.password_file = None
        # build widgets
        self.file_label = QLabel(f'Unlock "{os.path.basename(self.file_path)}"')
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pass_label = QLabel('Password:')
        self.pass_entry = QLineEdit()
        self.pass_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.accept_button = QPushButton('Accept')
        self.accept_button.clicked.connect(self.decrypt_passwords)
        self.file_select_button = QPushButton('Select another file')
        self.file_select_button.clicked.connect(self.select_file)
        # this label is only given text if the user inputs an incorrect password
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: #ff0000')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # create the main layout and display widgets
        self.main_layout = QGridLayout(self)
        self.main_layout.addWidget(self.file_label, 0, 0, 1, 2)
        self.main_layout.addWidget(self.pass_label, 1, 0, 1, 1)
        self.main_layout.addWidget(self.pass_entry, 1, 1, 1, 1)
        self.main_layout.addWidget(self.accept_button, 2, 0, 1, 2)
        self.main_layout.addWidget(self.file_select_button, 3, 0, 1, 2)
        self.main_layout.addWidget(self.error_label, 4, 0, 1, 2)
        self.setLayout(self.main_layout)

    def decrypt_passwords(self):
        # clear the error text if present
        self.error_label.setText('')
        try:
            # attempt to decrypt and initialize the password file with the user's provided password
            self.password_file = PasswordDatabase(self.file_path, self.pass_entry.text())
            self.password_file.load_file()
            self.close()
        except ValueError:
            self.attempts += 1
            self.password_file = None
            if self.attempts < 3:
                self.error_label.setText(f'Incorrect Password!\n{3 - self.attempts} {"attempts" if self.attempts < 2 else "attempt"} remaining')
            else:
                QErrorMessage().showMessage('An incorrect password was provided three times.\nThe program will now exit.')
                self.close()

    # selects a new file to attempt to decrypt, and reinitializes the dialog for that file 
    def select_file(self):
        file_name = file_path = QFileDialog.getOpenFileName(filter='Password Database Files (*.pwdb)')[0]
        if file_path: 
            self.file_path = file_path
            self.setWindowTitle(f'Unlock "{os.path.basename(self.file_path)}"')
            self.file_label.setText(f'Unlock "{os.path.basename(self.file_path)}"')


def show_login_prompt(file_path: str):
    app = QApplication(sys.argv)
    login = LoginWindow(file_path)
    login.show()
    app.exec()
    return login.password_file
