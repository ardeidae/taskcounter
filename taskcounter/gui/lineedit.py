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

"""Task counter custom line edit."""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QTextCursor, QTextOption
from PyQt5.QtWidgets import QCompleter, QTextEdit


class LineEdit(QTextEdit):
    """Custom LineEdit."""

    return_pressed = pyqtSignal()

    def __init__(self, parent=None):
        """Construct a custom line edit."""
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setUndoRedoEnabled(False)
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.completer = None
        self.textChanged.connect(self.__text_has_changed)

    def set_completer(self, completer):
        """Set the completer on the editor."""
        if completer:
            completer.setWidget(self)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setModelSorting(
                QCompleter.CaseSensitivelySortedModel)
            completer.setMaxVisibleItems(15)
            completer.activated.connect(self.__insert_completion)
            self.completer = completer

    @pyqtSlot(str)
    def __insert_completion(self, completion):
        """When the completer is activated, inserts the completion."""
        if self.completer and self.completer.widget() == self:
            self.completer.widget().setPlainText(completion)
            self.completer.widget().moveCursor(QTextCursor.EndOfLine)
            self.completer.widget().ensureCursorVisible()

    def keyPressEvent(self, event):
        """When a key is pressed."""
        if self.completer and self.completer.popup().isVisible():

            if event.key() in (Qt.Key_Return, Qt.Key_Enter,
                               Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Escape):
                event.ignore()
                return
        else:
            if event.key() in(Qt.Key_Return, Qt.Key_Enter):
                self.return_pressed.emit()
                return

        super().keyPressEvent(event)

        if not self.toPlainText():
            self.completer.popup().hide()
            return

        self.completer.setCompletionPrefix(self.toPlainText())
        self.completer.popup().setCurrentIndex(
            self.completer.completionModel().index(0, 0))
        self.completer.complete()

    @pyqtSlot()
    def __text_has_changed(self):
        """When the text has changed."""
        # remove new lines and strip left blank characters
        self.blockSignals(True)
        cursor_position = self.textCursor().position()

        origin = self.toPlainText()
        # count first whitespaces
        whitespaces = len(origin) - len(origin.lstrip())

        self.setPlainText(' '.join(origin.splitlines()).lstrip())
        cursor = self.textCursor()
        # to avoid offset when setting cursor position, substract whitespaces.
        cursor.setPosition(max(cursor_position - whitespaces, 0))
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self.blockSignals(False)
