import os
import sys
import pyperclip

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget, QListWidget, QPushButton, QLabel, QGridLayout, QMessageBox
from PySide6.QtCore import Qt

sys.path.append(os.path.abspath('src'))
from password_db import PasswordDatabase
from gui.create_password import PasswordCreationDialog
from gui.edit_password import PasswordEditDialog

class PasswordList(QWidget):
    def __init__(self, main_window, password_database):
        super().__init__()
        self.main_window = main_window
        self.password_database = password_database
        self.file_name = os.path.basename(self.password_database.file_path)
        self.saved = True
        # keyboard shortcuts
        self.delete_shortcut = QShortcut(QKeySequence('Delete'), self)
        self.delete_shortcut.activated.connect(self.delete_password)
        self.save_shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        self.save_shortcut.activated.connect(self.save_database)
        self.password_copy_shortcut = QShortcut(QKeySequence('Ctrl+C'), self)
        self.password_copy_shortcut.activated.connect(self.copy_password)
        self.username_copy_shortcut = QShortcut(QKeySequence('Ctrl+B'), self)
        self.username_copy_shortcut.activated.connect(self.copy_username)
        self.copy_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.copy_shortcut.activated.connect(self.close_window)
        self.init_ui()
        # child windows
        self.pass_create_dialog = None
        self.pass_edit_dialog = None
    
    def init_ui(self):
        # create widgets
        self.database_label = QLabel(self.file_name)
        self.database_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_list = QListWidget()
        self.password_list.insertItems(0, self.password_database.get_password_names())
        self.password_list.activated.connect(self.copy_password)
        self.password_list.itemClicked.connect(self.enable_buttons)
        self.copy_button = QPushButton('Copy')
        self.copy_button.clicked.connect(self.copy_password)
        self.copy_button.setEnabled(False)
        self.edit_button = QPushButton('Edit')
        self.edit_button.clicked.connect(self.edit_password)
        self.edit_button.setEnabled(False)
        self.new_button = QPushButton('New')
        self.new_button.clicked.connect(self.create_password)
        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_password)
        self.delete_button.setEnabled(False)
        self.save_button = QPushButton('Save Database')
        self.save_button.clicked.connect(self.save_database)
        # this label is only given text if the user provides invalid input
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: #ff0000')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # create the layout for the widget and place all widgets
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.database_label, 0, 0, 1, 2)
        self.layout.addWidget(self.password_list, 1, 0, 1, 2)
        self.layout.addWidget(self.copy_button, 2, 0, 1, 1)
        self.layout.addWidget(self.edit_button, 2, 1, 1, 1)
        self.layout.addWidget(self.new_button, 3, 0, 1, 1)
        self.layout.addWidget(self.delete_button, 3, 1, 1, 1)
        self.layout.addWidget(self.save_button, 4, 0, 1, 2)
        self.layout.addWidget(self.error_label, 5, 0, 1, 2)
        self.setLayout(self.layout)

    # marks that the password database has unsaved changes
    def mark_unsaved(self):
        self.main_window.setWindowTitle(f'• Passtore - {self.file_name}')
        self.saved = False

    # enables all of the buttons
    def enable_buttons(self):
        self.copy_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    # updates the password list to match the most recent changes to the database
    def update_password_list(self):
        self.mark_unsaved()
        self.password_list.clear()
        self.password_list.insertItems(0, self.password_database.get_password_names())

    # copies the currently selected password to the user's clipboard
    def copy_password(self):
        pyperclip.copy(self.password_database.get_password(self.password_list.currentItem().text()))

    # copies the username of the currently selected password to the user's clipboard
    def copy_username(self):
        # this uses -1 and index as opposed to just 1 to account for site names with dashes
        pyperclip.copy(self.password_list.currentItem().text().split('-')[-1].strip())

    # opens a dialog that allows the user to edit the currently selected password
    def edit_password(self):
        password_name = self.password_list.currentItem().text()
        if not self.pass_edit_dialog:
            self.pass_edit_dialog = PasswordEditDialog(self, password_name)
        else:
            site_name, username = map(lambda x: x.strip(), password_name.split('-'))
            # redraw the widget for this password
            self.pass_edit_dialog.password_name = password_name
            self.pass_edit_dialog.setWindowTitle(f'Editing password for "{site_name}"')
            self.pass_edit_dialog.title_label.setText(f'Editing password for "{site_name}"')
            self.pass_edit_dialog.site_name_entry.setText(site_name)
            self.pass_create_dialog.username_entry.setText(username)
            self.pass_edit_dialog.pass_entry.setText(self.password_database.get_password(password_name))
            self.pass_edit_dialog.confirm_entry.setText(self.password_database.get_password(password_name))
        self.pass_edit_dialog.show()

    # opens a dialog that allows the user to create a new password
    def create_password(self):
        if not self.pass_create_dialog:
            self.pass_create_dialog = PasswordCreationDialog(self)
        self.pass_create_dialog.show()

    # deletes the currently selected password
    def delete_password(self):
        self.password_database.delete_password(self.password_list.currentItem().text())
        self.mark_unsaved()
        self.update_password_list()

    # saves the password database file
    def save_database(self):
        self.saved = True
        self.main_window.setWindowTitle(f'Passtore - {self.file_name}')
        self.password_database.save_file()

    # closes the application
    def close_window(self):
        if not self.saved:
            msgBox = QMessageBox()
            msgBox.setText("The database has been modified. Please save it before exiting")
            msgBox.exec_()
            return 
        self.main_window.close()
