import os
import sys
import json

from PySide6.QtWidgets import QApplication, QErrorMessage

from gui.login import show_login_prompt
from gui.create_file import FileCreationDialog
from gui.main_window import MainWindow

PASSTORE_PATH = os.path.join(os.path.expanduser('~'), '.passtore')
# check if the user has a prefs file, run the initalization for the first password file
if not os.path.exists(PASSTORE_PATH):
    app = QApplication()
    dialog = FileCreationDialog()
    dialog.show()
    app.exec()
    # create the user prefernces if a password database was created
    if os.path.exists(dialog.file_path):
        os.mkdir(f'{PASSTORE_PATH}')
        with open(f'{PASSTORE_PATH}/prefs.json', 'w') as p:
            json.dump({'last_modified':  dialog.file_path}, p)
else:
    # read the user's preferences
    with open(f'{PASSTORE_PATH}/prefs.json') as p:
        prefs = json.load(p)
    # attempt to decrypt the password file
    last_modified = prefs['last_modified']
    if os.path.exists(last_modified):
        password_file =  show_login_prompt(last_modified)
        if password_file:
            # update the user preferences if a new file was selected
            if password_file.file_path != prefs['last_modified']:
                prefs['last_modified'] = password_file.file_path
                with open(os.path.join(PASSTORE_PATH, 'prefs.json'), 'w') as p:
                    json.dump(prefs, p)
            app = QApplication.instance()
            main_window = MainWindow(password_file)
            main_window.show()
            sys.exit(app.exec())
    else:
        app = QApplication()
        err = QErrorMessage()
        err.showMessage(f'The file "{last_modified}" could not be found. Please create a new password database.')
        err.show()
        dialog = FileCreationDialog()
        dialog.show()
        sys.exit(app.exec())
