from PyQt5.QtCore import QEvent, QRegExp, QSize, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QRegExpValidator, QValidator
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
            '^[0-9]{1,' + str(self._hour_length) + '}:[0-5]{,1}[0-9]$')
        self._validator = QRegExpValidator(regexp)
        self._minutes = 0
        self.lineEdit().textChanged.connect(self.text_changed)

    def __text__(self):
        """Get the line edit text."""
        return self.lineEdit().text()

    def __cursor_position__(self):
        """Get the cursor position."""
        return self.lineEdit().cursorPosition()

    def __max_hours__(self):
        """Get the max hours that can be reached for the hour length."""
        return 10 ** self._hour_length - 1

    def validate(self, text, pos):
        """Determine whether input is valid."""
        return self._validator.validate(text, pos)

    @staticmethod
    def minutesToText(minutes):
        """Convert minutes to a time string."""
        return '{:02d}:{:02d}'.format(*divmod(minutes, 60))

    @staticmethod
    def textToMinutes(text):
        """Convert time text to minutes."""
        hours = minutes = 0
        try:
            array = text.split(':')
            hours = array[0]
            minutes = array[1]
        except (IndexError, ValueError):
            pass

        hours = 0 if not hours else hours
        minutes = 0 if not minutes else minutes

        return int(hours) * 60 + int(minutes)

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
            if hours > self.__max_hours__():
                self._minutes = 0
                self.valueChanged.emit(self._minutes)
            else:
                self._minutes = minutes
                self.valueChanged.emit(self._minutes)
        self.lineEdit().setText(self.minutesToText(self._minutes))

    def stepBy(self, steps):
        """Trigger a step."""
        cursor_position = self.__cursor_position__()
        text = self.__text__()
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
        cursor_position = self.__cursor_position__()
        text = self.__text__()
        try:
            index = text.index(':')
        except ValueError:
            try:
                hours = int(text)
            except ValueError:
                pass
            else:
                # we have only hours in the field
                if hours <= 0:
                    return QAbstractSpinBox.StepUpEnabled
                elif hours >= self.__max_hours__():
                    return QAbstractSpinBox.StepDownEnabled
                else:
                    return (QAbstractSpinBox.StepUpEnabled |
                            QAbstractSpinBox.StepDownEnabled)
        else:
            hours = int(text[:index])
            minutes = int(text[index + 1:])
            if 0 <= cursor_position <= index:
                if hours <= 0:
                    return QAbstractSpinBox.StepUpEnabled
                elif hours >= self.__max_hours__():
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
            text = self.__text__()
            key = event.key()
            try:
                index = text.index(':')
            except ValueError:
                if key in (Qt.Key_Tab, Qt.Key_Backtab):
                    self.lineEdit().setText(self.minutesToText(self._minutes))
            else:
                cursor_position = self.__cursor_position__()
                if key == Qt.Key_Colon:
                    if cursor_position <= index:
                        self.lineEdit().setSelection(index + 1, len(text))
                        return True
                    else:
                        return False
                if key == Qt.Key_Tab:
                    if cursor_position <= index:
                        self.lineEdit().setSelection(index + 1, len(text))
                        return True
                    else:
                        self.lineEdit().setText(self.minutesToText(
                            self._minutes))
                        return super().event(event)
                elif key == Qt.Key_Backtab:
                    if cursor_position > index:
                        self.lineEdit().setSelection(0, index)
                        return True
                    else:
                        self.lineEdit().setText(self.minutesToText(
                            self._minutes))
                        return super().event(event)

        return super().event(event)

    def focusOutEvent(self, event):
        """Receive keyboard focus events (focus lost) for the widget."""
        super().focusOutEvent(event)

        self.lineEdit().setText(self.minutesToText(self._minutes))

    def focusInEvent(self, event):
        """Receive keyboard focus events (focus received) for the widget."""
        super().focusInEvent(event)

        text = self.__text__()
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
        self._minutes = self.textToMinutes(text)

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
