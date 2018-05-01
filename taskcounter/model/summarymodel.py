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

"""Task counter summary model."""

from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant

from taskcounter.enum import ResultColumn
from taskcounter.utility import minutes_to_time_str


class SummaryModel(QAbstractTableModel):
    """Result summary model."""

    def __init__(self, parent=None):
        """Construct a result summary object."""
        super().__init__(parent)

        self._tasks = []
        self._manday_minutes = 0

    def rowCount(self, parent=None):
        """Return the number of rows under the given parent."""
        return len(self._tasks)

    def columnCount(self, parent=None):
        """Return the number of columns under the given parent."""
        return len(ResultColumn)

    @property
    def tasks(self):
        """Get the tasks."""
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        """Set the tasks."""
        self.layoutAboutToBeChanged.emit()

        self._tasks = tasks

        top_left = self.index(0, 0)
        bottom_right = self.index(
            self.rowCount() + 1, self.columnCount())
        self.dataChanged.emit(
            top_left, bottom_right, [Qt.DisplayRole])

        self.layoutChanged.emit()

    @property
    def manday_minutes(self):
        """Get the manday minutes."""
        return self._manday_minutes

    @manday_minutes.setter
    def manday_minutes(self, manday_minutes):
        """Set the manday minutes."""
        self._manday_minutes = manday_minutes

    def data(self, index, role):
        """Return the data.

        Return the data stored under the given role for the item referred
        to by the index.
        """
        if not index.isValid():
            return QVariant()

        row = index.row()
        column = index.column()
        if role in (Qt.DisplayRole, Qt.ToolTipRole):
            try:
                value = self._tasks[row][ResultColumn(column)]
            except KeyError:
                return QVariant()
            else:
                if column == ResultColumn.Task.value:
                    if role == Qt.ToolTipRole:
                        # html text allows automatic word-wrapping on tooltip.
                        return '<html>{}</html>'.format(str(value))
                    else:
                        return str(value)
                elif column == ResultColumn.Time.value:
                    return minutes_to_time_str(value)
                elif column == ResultColumn.Man_Day.value:
                    return value
        elif role == Qt.TextAlignmentRole:
            if column == ResultColumn.Task.value:
                return Qt.AlignLeft | Qt.AlignVCenter
            else:
                return Qt.AlignCenter | Qt.AlignVCenter

        return QVariant()

    def headerData(self, section, orientation, role):
        """Return the header data.

        Return the data for the given role and section in the header with
        the specified orientation.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ResultColumn(section).name.replace('_', ' ')
        return QVariant()
