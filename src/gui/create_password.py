import sys

from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QSlider
from PySide6.QtCore import Qt

sys.path.append('src')
from password_db import PasswordDatabase

class PasswordCreationDialog(QWidget):
    def __init__(self,  parent_widget):
        super().__init__()
        self.setWindowTitle('Create a password')
        self.parent_widget = parent_widget
        self.init_dialog()

    def init_dialog(self):
        # create widgets
        self.title_label = QLabel('Create a password', parent=self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.site_name_label = QLabel('Site Name:', parent=self)
        self.site_name_entry = QLineEdit(self)
        self.pass_label = QLabel('Password:', parent=self)
        self.confirm_label = QLabel('Confirm:')
        self.pass_entry = QLineEdit(self)
        self.pass_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_entry = QLineEdit(self)
        self.confirm_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.slider_name_label = QLabel('Password Size:', parent=self)
        self.slider_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_slider = QSlider(Qt.Orientation.Horizontal, parent=self)
        self.size_slider.setMinimum(8)
        self.size_slider.setMaximum(24)
        self.size_slider.setValue(16)
        self.size_slider.valueChanged.connect(self.update_slider)
        self.size_label = QLabel('16', parent=self)
        self.accept_button = QPushButton('Accept', parent=self)
        self.accept_button.clicked.connect(self.create_password)
        self.cancel_button = QPushButton('Cancel', parent=self)
        self.cancel_button.clicked.connect(self.close)
        # generate a password
        self.generate_password(16)
        # this label is only given text if the user provides invalid input
        self.error_label = QLabel('', parent=self)
        self.error_label.setStyleSheet('color: #ff0000')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # create the layout for the widget and place all widgets
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.title_label, 0, 0, 1, 3)
        self.layout.addWidget(self.site_name_label, 1, 0, 1, 1)
        self.layout.addWidget(self.site_name_entry, 1, 1, 1, 1)
        self.layout.addWidget(self.pass_label, 2, 0, 1, 1)
        self.layout.addWidget(self.pass_entry, 2, 1, 1, 1)
        self.layout.addWidget(self.confirm_label, 3, 0, 1, 1)
        self.layout.addWidget(self.confirm_entry, 3, 1, 1, 1)
        self.layout.addWidget(self.slider_name_label, 4, 0, 1, 3)
        self.layout.addWidget(self.size_slider, 5, 0, 1, 2)
        self.layout.addWidget(self.size_label, 5, 2, 1, 1)
        self.layout.addWidget(self.cancel_button, 6, 0, 1, 1)
        self.layout.addWidget(self.accept_button, 6, 1, 2, 1)
        self.setLayout(self.layout)

    # create the new password and save it to the password database
    def create_password(self):
        # clear the error text, if present
        self.error_label.setText('')
        site_name = self.site_name_entry.text()
        password = self.pass_entry.text()
        # verify that the password matches the confirmation
        if password != self.confirm_entry.text():
            self.error_label.setText('Password and confirmation must match')
            return 
        # ensure that the site name for the password is unused
        if password in self.parent_widget.password_database.passwords.keys():
            self.error_label.setText(f'A password for "{site_name}" already exists in this database')
            return 
        # reset the entries to defaults for the user's next password
        self.site_name_entry.setText('')
        self.size_slider.setValue(16)
        self.generate_password(16)
        # update the parent widget's UI
        self.parent_widget.password_database.add_password(site_name, password)
        self.parent_widget.update_password_list()
        self.close()

    # generates a random password of a user-specified size
    def generate_password(self, size: int):
        password = PasswordDatabase.generate_password(size)
        self.pass_entry.setText(password)
        self.confirm_entry.setText(password)

    # updates the text to the QSlider, and generates a new password of an appropriate size
    def update_slider(self):
        pass_size = self.size_slider.value()
        self.size_label.setText(str(pass_size))
        self.generate_password(pass_size)