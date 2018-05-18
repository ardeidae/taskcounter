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

"""Task counter about dialog."""

import logging

from PyQt5.QtCore import QFile, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QTabWidget,
                             QTextBrowser, QVBoxLayout)

from taskcounter.version import author, github_repository, version

from .centermixin import CenterMixin


class AboutDialog(CenterMixin, QDialog):
    """Application about dialog."""

    def __init__(self, parent=None):
        """Construct an about dialog."""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Opening about dialog')
        self.setWindowTitle('About this software')
        self.setMinimumHeight(600)
        self.setMinimumWidth(600)
        self.center()

        self.license = self.__build_text_browser__()
        self.about = self.__build_text_browser__()

        repository_label = QLabel(
            '<html>Source repository URL: <a href="{link}">{link}</a></html>'
            .format(link=github_repository), self)
        repository_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        repository_label.setOpenExternalLinks(True)
        author_label = QLabel('Author: {}'.format(author))
        version_label = QLabel(
            'Version: {}'.format(version), self)

        self.tab_widget = QTabWidget(self)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(repository_label)
        layout.addWidget(author_label)
        layout.addWidget(version_label)
        layout.addWidget(self.tab_widget)

        self.tab_widget.addTab(self.license, 'License')
        self.tab_widget.addTab(self.about, 'Third-Party Software Notices')

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.license.setText(self.__get_file_content__(':/LICENSE'))
        self.about.setText(self.__get_file_content__(':/ABOUT'))

    @staticmethod
    def __build_text_browser__():
        """Build a text browser."""
        edit = QTextBrowser()
        edit.setReadOnly(True)
        edit.setOpenExternalLinks(True)
        font = QFont('Courier')
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(11)
        font.setFixedPitch(True)
        edit.setFont(font)
        return edit

    @staticmethod
    def __get_file_content__(resource_file):
        """Get the content of a given resource file."""
        logger = logging.getLogger(__name__)
        file = QFile(resource_file)
        logger.info('Opening read only file: %s', resource_file)
        if file.open(QFile.ReadOnly):
            string = str(file.readAll(), 'utf-8')
            file.close()
            logger.info('File closed')
            logger.debug('Returning: %s', string)
            return str(string)
        else:
            logger.error('Error opening file: %s. Error: %s',
                         resource_file, file.errorString)
            logger.debug('Returning empty string')
            return ''
