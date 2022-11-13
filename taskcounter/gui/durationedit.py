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

"""Task counter duration edit."""

from PyQt5.QtCore import QEvent, QRegExp, QSize, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (QAbstractSpinBox, QApplication, QStyle,
                             QStyleOptionSpinBox)


class DurationEdit(QAbstractSpinBox):
    """Duration edit."""

    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None, hour_length=2):
        """Construct a duration edit."""
        super().__init__(parent)
        self._hour_length = hour_length
        regexp = QRegExp(
            '^[0-9]{1,' + str(self._hour_length) + '}:[0-5]{,1}[0-9]?$')
        self._validator = QRegExpValidator(regexp)
        self._minutes = 0
        self.lineEdit().textChanged.connect(self.text_changed)

    def __text(self):
        """Get the line edit text."""
        return self.lineEdit().text()

    def __cursor_position(self):
        """Get the cursor position."""
        return self.lineEdit().cursorPosition()

    def __max_hours(self):
        """Get the max hours that can be reached for the hour length."""
        return 10 ** self._hour_length - 1

    def validate(self, text, pos):
        """Determine whether input is valid."""
        return self._validator.validate(text, pos)

    @staticmethod
    def minutes_to_text(minutes):
        """Convert minutes to a time string."""
        return '{:02d}:{:02d}'.format(*divmod(minutes, 60))

    @staticmethod
    def text_to_minutes(text):
        """Convert time text to minutes."""
        minutes = 0
        array = text.split(':')
        try:
            hours = int(array[0])
        except ValueError:
            hours = 0
        if len(array) == 2:
            try:
                minutes = int(array[1])
            except ValueError:
                minutes = 0

        return hours * 60 + minutes

    @property
    def minutes(self):
        """Get the total minutes."""
        return self._minutes

    @minutes.setter
    def minutes(self, minutes):
        """Set the total minutes."""
        try:
            minutes = int(minutes)
        except TypeError:
            self._minutes = 0
            self.valueChanged.emit(self._minutes)
        else:
            hours = divmod(minutes, 60)[0]
            if hours > self.__max_hours():
                self._minutes = 0
                self.valueChanged.emit(self._minutes)
            else:
                self._minutes = minutes
                self.valueChanged.emit(self._minutes)
        self.lineEdit().setText(self.minutes_to_text(self._minutes))

    def stepBy(self, steps):
        """Trigger a step."""
        cursor_position = self.__cursor_position()
        text = self.__text()
        try:
            index = text.index(':')
        except ValueError:
            # we have only hours in the field
            self.minutes = self.minutes + steps * 60
        else:
            value = 0
            if 0 <= cursor_position <= index:
                value = steps * 60
            elif index + 1 <= cursor_position <= len(text):
                value = steps
            self.minutes = self.minutes + value

        self.lineEdit().setCursorPosition(cursor_position)

    def stepEnabled(self):
        """Determine whether stepping up and down is legal at any time."""
        cursor_position = self.__cursor_position()
        text = self.__text()
        try:
            index = text.index(':')
        except ValueError:
            # no : in string
            try:
                hours = int(text)
            except ValueError:
                hours = 0

            # we have only hours in the field
            if hours <= 0:
                return QAbstractSpinBox.StepUpEnabled
            elif hours >= self.__max_hours():
                return QAbstractSpinBox.StepDownEnabled
            else:
                return (QAbstractSpinBox.StepUpEnabled |
                        QAbstractSpinBox.StepDownEnabled)
        else:
            try:
                hours = int(text[:index])
            except ValueError:
                hours = 0
            try:
                minutes = int(text[index + 1:])
            except ValueError:
                minutes = 0

            if 0 <= cursor_position <= index:
                if hours <= 0:
                    return QAbstractSpinBox.StepUpEnabled
                elif hours >= self.__max_hours():
                    return QAbstractSpinBox.StepDownEnabled
                else:
                    return (QAbstractSpinBox.StepUpEnabled |
                            QAbstractSpinBox.StepDownEnabled)
            elif index + 1 <= cursor_position <= len(text):
                if minutes <= 0:
                    return QAbstractSpinBox.StepUpEnabled
                elif minutes >= 59:
                    return QAbstractSpinBox.StepDownEnabled
                else:
                    return(QAbstractSpinBox.StepUpEnabled |
                           QAbstractSpinBox.StepDownEnabled)

        return QAbstractSpinBox.StepNone

    def event(self, event):
        """Handle event and check for Tab and Shift+Tab."""
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key in (Qt.Key_Enter, Qt.Key_Return):
                self.minutes = self.text_to_minutes(self.__text())
                return super().event(event)

            text = self.__text()
            try:
                index = text.index(':')
            except ValueError:
                # no : in string, on tab or backtab, go to next field, but
                # format this one before
                if key in (Qt.Key_Tab, Qt.Key_Backtab):
                    self.minutes = self.text_to_minutes(self.__text())
                    return super().event(event)
            else:
                cursor_position = self.__cursor_position()
                if key == Qt.Key_Colon:
                    # go to minutes on : type if cursor is on hours
                    if cursor_position <= index:
                        self.lineEdit().setSelection(index + 1, len(text))
                        return True
                    else:
                        return False
                if key == Qt.Key_Tab:
                    if cursor_position <= index:
                        # go to minutes on tab
                        self.lineEdit().setSelection(index + 1, len(text))
                        return True
                    else:
                        # go to next field on tab, but update minutes before
                        self.minutes = self.text_to_minutes(self.__text())
                        return super().event(event)
                elif key == Qt.Key_Backtab:
                    if cursor_position > index:
                        # go to hours on backtab
                        self.lineEdit().setSelection(0, index)
                        return True
                    else:
                        # go to previous field on backtab, but update minutes
                        # before
                        self.minutes = self.text_to_minutes(self.__text())
                        return super().event(event)

        if event.type() == QEvent.KeyRelease:
            # on [0-9] key release, if hours are filled, go to minutes
            if event.key() in (Qt.Key_0, Qt.Key_1, Qt.Key_3, Qt.Key_2,
                               Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7,
                               Qt.Key_8, Qt.Key_9):
                text = self.__text()
                try:
                    index = text.index(':')
                except ValueError:
                    pass
                else:
                    cursor_position = self.__cursor_position()
                    if index == cursor_position == self._hour_length:
                        self.lineEdit().setSelection(index + 1, len(text))
                        return True

        return super().event(event)

    def focusOutEvent(self, event):
        """Receive keyboard focus events (focus lost) for the widget."""
        super().focusOutEvent(event)

        self.minutes = self.text_to_minutes(self.__text())

    def focusInEvent(self, event):
        """Receive keyboard focus events (focus received) for the widget."""
        super().focusInEvent(event)

        text = self.__text()
        reason = event.reason()
        try:
            index = text.index(':')
        except ValueError:
            pass
        else:
            if reason == Qt.BacktabFocusReason:
                self.lineEdit().setSelection(index + 1, len(text))
            elif reason == Qt.TabFocusReason:
                self.lineEdit().setSelection(0, index)

    @pyqtSlot(str)
    def text_changed(self, text):
        """Update the stored value."""
        self._minutes = self.text_to_minutes(text)

    def sizeHint(self):
        """Return the recommended size for the widget."""
        string = '_' * self._hour_length + ':__ '
        fm = self.fontMetrics()
        height = self.lineEdit().sizeHint().height()
        width = fm.width(string) + 12

        hint = QSize(width, height)
        option = QStyleOptionSpinBox()
        return (self.style()
                .sizeFromContents(QStyle.CT_SpinBox, option, hint,
                                  self)
                .expandedTo(QApplication.globalStrut()))
