import sys

from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGridLayout
from PySide6.QtCore import Qt

class PasswordEditDialog(QWidget):
    def __init__(self, parent_widget, site_name: str):
        super().__init__()
        self.parent_widget = parent_widget
        self.site_name = site_name
        self.password = self.parent_widget.password_database.get_password(site_name)
        self.setWindowTitle(f'Editing password for "{self.site_name}"')
        self.init_dialog()

    def init_dialog(self):
        # create widgets
        self.title_label = QLabel(f'Editing password for "{self.site_name}"')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.site_name_label = QLabel('Site Name:')
        self.site_name_entry = QLineEdit()
        self.site_name_entry.setText(self.site_name)
        self.pass_label = QLabel('Password:', parent=self)
        self.confirm_label = QLabel('Confirm:')
        self.pass_entry = QLineEdit(self)
        self.pass_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_entry.setText(self.password)
        self.confirm_entry = QLineEdit(self)
        self.confirm_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_entry.setText(self.password)
        self.confirm_button = QPushButton('Confirm')
        self.confirm_button.clicked.connect(self.confirm)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.close)
        # this label is only given text if the user provides invalid input
        self.error_label = QLabel('', parent=self)
        self.error_label.setStyleSheet('color: #ff0000')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # create the layout for the widget and place all widgets
        self.layout = QGridLayout()
        self.layout.addWidget(self.title_label, 0, 0, 1, 2)
        self.layout.addWidget(self.site_name_label, 1, 0, 1, 1)
        self.layout.addWidget(self.site_name_entry, 1, 1, 1, 1)
        self.layout.addWidget(self.pass_label, 2, 0, 1, 1)
        self.layout.addWidget(self.pass_entry, 2, 1, 1, 1)
        self.layout.addWidget(self.confirm_label, 3, 0, 1, 1)
        self.layout.addWidget(self.confirm_entry, 3, 1, 1, 1)
        self.layout.addWidget(self.cancel_button, 4, 0, 1, 1)
        self.layout.addWidget(self.confirm_button, 4, 1, 1, 1)
        self.layout.addWidget(self.error_label, 5, 0, 1, 1)
        self.setLayout(self.layout)

    def confirm(self):
        password = self.pass_entry.text()
        # clear the error text, if present
        self.error_label.setText('')
        if self.site_name != self.site_name_entry.text():
            new_name = self.site_name_entry.text()
            renamed = True
        else:
            new_name = None
            renamed = False
        # if the password is to be renamed, verify that the name will not overwrite any existing passwords
        if renamed and new_name in self.parent_widget.password_database.get_site_names():
                self.error_label.setText(f'A password for the site "{new_name}" already exists')
                return 
        # verify that the password matches the confirmation
        if password != self.confirm_entry.text():
            self.error_label.setText('Password and confirmation must match')
            return 
        self.parent_widget.password_database.update_password(self.site_name, password)
        if renamed:
            self.parent_widget.password_database.rename_password(self.site_name, new_name)
        self.parent_widget.update_password_list()
        self.close()


