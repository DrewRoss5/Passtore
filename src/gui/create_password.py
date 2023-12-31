import sys

from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QSlider, QProgressBar
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
        self.title_label = QLabel('Create a password')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.site_name_label = QLabel('Site Name:')
        self.site_name_entry = QLineEdit(self)
        self.username_label = QLabel('Username:')
        self.username_entry = QLineEdit()
        self.pass_label = QLabel('Password:')
        self.confirm_label = QLabel('Confirm:')
        self.pass_entry = QLineEdit()
        self.pass_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_entry.textChanged.connect(self.update_password)
        self.confirm_entry = QLineEdit()
        self.confirm_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_entry.textChanged.connect(self.update_password)
        self.strength_bar = QProgressBar()
        self.strength_label = QLabel('Strength:')
        self.strength_bar.setRange(0, 50)
        self.slider_name_label = QLabel('Password Size:')
        self.slider_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(8)
        self.size_slider.setMaximum(24)
        self.size_slider.setValue(16)
        self.size_slider.valueChanged.connect(self.generate_password)
        self.size_label = QLabel('16', parent=self)
        self.accept_button = QPushButton('Accept', parent=self)
        self.accept_button.clicked.connect(self.create_password)
        self.cancel_button = QPushButton('Cancel', parent=self)
        self.cancel_button.clicked.connect(self.close)
        # this label is only given text if the user provides invalid input
        self.error_label = QLabel('', parent=self)
        self.error_label.setStyleSheet('color: #ff0000')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # create the layout for the widget and place all widgets
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.title_label, 0, 0, 1, 3)
        self.layout.addWidget(self.site_name_label, 1, 0, 1, 1)
        self.layout.addWidget(self.site_name_entry, 1, 1, 1, 1)
        self.layout.addWidget(self.username_label, 2, 0, 1, 1)
        self.layout.addWidget(self.username_entry, 2, 1, 1, 1)
        self.layout.addWidget(self.pass_label, 3, 0, 1, 1)
        self.layout.addWidget(self.pass_entry, 3, 1, 1, 1)
        self.layout.addWidget(self.confirm_label, 4, 0, 1, 1)
        self.layout.addWidget(self.confirm_entry, 4, 1, 1, 1)
        self.layout.addWidget(self.strength_label, 5, 0, 1, 1)
        self.layout.addWidget(self.strength_bar, 5, 1, 1, 2)
        self.layout.addWidget(self.slider_name_label, 6, 0, 1, 3)
        self.layout.addWidget(self.size_slider, 7, 0, 1, 2)
        self.layout.addWidget(self.size_label, 7, 2, 1, 1)
        self.layout.addWidget(self.cancel_button, 8, 0, 1, 1)
        self.layout.addWidget(self.accept_button, 8, 1, 1, 2)
        self.layout.addWidget(self.error_label, 9, 0, 1, 3)
        self.setLayout(self.layout)
        # generate a random password
        self.generate_password()

    # create the new password and save it to the password database
    def create_password(self):
        # clear the error text, if present
        self.error_label.setText('')
        # collect password attributes from the entries
        site_name = self.site_name_entry.text()
        password = self.pass_entry.text()
        username = self.username_entry.text()
        password_key = f'{site_name} - {username}'
        # ensure that the site name for the password is unused
        if f'{site_name} - {username}' in self.parent_widget.password_database.get_password_names():
            self.error_label.setText(f'A password for that username and site combination already exists in this database')
            return 
        # ensure that the username does not include a '!'
        if '!' in username:
            self.error_label.setText(f'The username may not contain "!"')
        # reset the entries to defaults for the user's next password
        self.site_name_entry.setText('')
        self.username_entry.setText('')
        self.size_slider.setValue(16)
        self.generate_password()
        # update the parent widget's UI
        self.parent_widget.password_database.add_password(site_name, username, password)
        self.parent_widget.update_password_list()
        self.close()

    # updates the text to the QSlider, and generates a new password of an appropriate size
    def generate_password(self):
        pass_size = self.size_slider.value()
        self.size_label.setText(str(pass_size))
        # generate a new passsword and place into the entries
        password = PasswordDatabase.generate_password(pass_size)
        self.pass_entry.setText(password)
        self.confirm_entry.setText(password)
        self.update_password()

    def update_password(self):
        # update the password strength meter
        password_strength = PasswordDatabase.grade_password(self.pass_entry.text())
        self.strength_bar.setValue(password_strength)
        self.strength_bar.setFormat(str(password_strength))
        # ensure the password and confirmation match
        if (self.pass_entry.text() != self.confirm_entry.text()):
            self.error_label.setText('Password and Confirmation must match')
            self.accept_button.setEnabled(False)
        else:
            self.error_label.setText('')
            self.accept_button.setEnabled(True)

    
