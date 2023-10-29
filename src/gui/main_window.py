import os
import sys
import pyperclip

from PySide6.QtWidgets import QMainWindow

sys.path.append(os.path.abspath('src'))
from password_db import PasswordDatabase
from gui.create_password import PasswordCreationDialog
from gui.password_list import PasswordList

class MainWindow(QMainWindow):
    def __init__(self, password_database: PasswordDatabase):
        super().__init__()
        self.password_list = PasswordList(self, password_database)
        self.setCentralWidget(self.password_list)
        self.setWindowTitle(f'Passtore - {self.password_list.file_name}')
       
   