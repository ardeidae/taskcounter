"""Tasks counter main entry point."""

import sys

from PyQt5.QtWidgets import QApplication

from gui import MainWindow, create_database

if __name__ == '__main__':
    app = QApplication(sys.argv)

    create_database()

    mw = MainWindow()
    mw.initUI()

    sys.exit(app.exec_())
