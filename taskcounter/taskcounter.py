#     Copyright (C) 2018  Matthieu PETIOT
#
#     https://github.com/ardeidae/taskcounter
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Task counter main entry point."""

import logging
import sys

from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import QApplication

from taskcounter import resources
from taskcounter.db import create_database
from taskcounter.gui import MainWindow


def main():
    """Start the application."""
    logger = logging.getLogger(__name__)

    logger.info('Starting application')

    app = QApplication(sys.argv)

    locale = QLocale.system().name()
    logger.info('Locale: ' + locale)
    translation_file = ':/{}.qm'.format(locale)
    logger.info('Translation file: ' + translation_file)

    translator = QTranslator()
    if translator.load(translation_file):
        logger.info('Translator loaded. Installing...')
        app.installTranslator(translator)
    else:
        logger.warning('Unable to load translator')

    create_database()

    main_window = MainWindow()
    main_window.init_ui()

    return app.exec_()
