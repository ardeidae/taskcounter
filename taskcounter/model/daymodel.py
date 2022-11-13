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

"""Task counter day model."""

import logging

from PyQt5.QtCore import QAbstractTableModel, Qt, QTime, QVariant
from PyQt5.QtGui import QBrush, QColor

from taskcounter.db import SQL, Day, IntegrityError, Task, fn
from taskcounter.enum import TaskColumn
from taskcounter.utility import contrast_color
from taskcounter.model import SettingModel


class DayModel(QAbstractTableModel):
    """Wrapper for the day model."""

    def __init__(self, date_, week, parent=None):
        """Construct a day wrapper object."""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self._day = Day.get_or_create(date=date_,
                                      week=week)[0]
        self._cached_data = None
        self.__cache_data()

    @property
    def week(self):
        """Get the week property."""
        return self._day.week

    @property
    def date(self):
        """Get the date property."""
        return self._day.date

    def rowCount(self, parent=None, *args, **kwargs):
        """Return the number of rows under the given parent."""
        return len(self._cached_data) + 1

    def columnCount(self, parent=None, *args, **kwargs):
        """Return the number of columns under the given parent."""
        return len(TaskColumn)

    def __cache_data(self):
        """Cache data."""
        self._cached_data = {}

        # ensure that null start_time appears in last positions
        for counter, task in enumerate(Task.select(Task.id, Task.name,
                                                   Task.start_time,
                                                   Task.end_time)
                                       .join(Day)
                                       .where(Task.day == self._day)
                                       .order_by(SQL(
                                           "IFNULL(start_time, '24:00')"
                                       ))):
            row = {
                TaskColumn.Id: task.id,
                TaskColumn.Task: task.name,
                TaskColumn.Start_Time: task.start_time,
                TaskColumn.End_Time: task.end_time
            }
            self._cached_data[counter] = row
            self.logger.debug('Cached data: %s', self._cached_data)

    def get_cached_data(self, row, column):
        """Get the cached data for a given row and column."""
        try:
            return self._cached_data[row][column]
        except KeyError:
            return ''

    def data(self, index, role=None):
        """Return the data.

        Return the data stored under the given role for the item referred
        to by the index.
        """
        if not index.isValid():
            return QVariant()

        row = index.row()
        column = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole):
            try:
                value = self._cached_data[row][TaskColumn(column)]
            except KeyError:
                return QVariant()
            else:
                if column == TaskColumn.Id.value:
                    return int(value)
                elif column == TaskColumn.Task.value:
                    if role == Qt.ToolTipRole:
                        # html text allows automatic word-wrapping on tooltip.
                        return '<html>{}</html>'.format(str(value))
                    else:
                        return str(value)
                elif column in (TaskColumn.Start_Time.value,
                                TaskColumn.End_Time.value):
                    try:
                        a_time = QTime(value.hour, value.minute, value.second)
                        return QVariant(a_time)
                    except AttributeError:
                        if role == Qt.EditRole:
                            return QVariant(QTime(0, 0))
                        else:
                            return QVariant()
        elif role in (Qt.BackgroundRole, Qt.ForegroundRole):
            try:
                start = self._cached_data[row][TaskColumn.Start_Time]
                end = self._cached_data[row][TaskColumn.End_Time]
                background_color = SettingModel.valid_color()
                if role == Qt.BackgroundRole:
                    if not start or not end or start >= end:
                        background_color = SettingModel.invalid_color()
                    return QBrush(background_color)
                elif role == Qt.ForegroundRole:
                    text_color = contrast_color(background_color.name())
                    return QBrush(QColor(text_color))
            except KeyError:
                pass

        elif role == Qt.TextAlignmentRole:
            if column == TaskColumn.Task.value:
                return Qt.AlignLeft | Qt.AlignVCenter
            else:
                return Qt.AlignCenter | Qt.AlignVCenter

        return QVariant()

    def setData(self, index, value, role=None):
        """Set the role data for the item at index to value."""
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()

            field = TaskColumn(column)

            if row in self._cached_data:
                task_id = self._cached_data[row][TaskColumn.Id]

                if field == TaskColumn.Task and not value:
                    if self.delete_task(task_id):
                        self.__cache_data()
                        self.layoutAboutToBeChanged.emit()
                        top_left = self.index(0, 0)
                        bottom_right = self.index(
                            self.rowCount() + 1, self.columnCount())
                        self.dataChanged.emit(top_left, bottom_right,
                                              [Qt.DisplayRole])
                        self.layoutChanged.emit()
                        return True
                else:
                    if not value:
                        return False

                    if field == TaskColumn.Start_Time:
                        end = self._cached_data[row][TaskColumn.End_Time]
                        if end and value >= end:
                            return False
                    elif field == TaskColumn.End_Time:
                        start = self._cached_data[row][TaskColumn.Start_Time]
                        if start and value <= start:
                            return False
                    if field in (TaskColumn.Start_Time, TaskColumn.End_Time):
                        if self.__overlaps_other_range(task_id,
                                                       field, value):
                            return False

                    if self.update_task(task_id, field, value):
                        self.__cache_data()

                        self.layoutAboutToBeChanged.emit()
                        top_left = self.index(0, 0)
                        bottom_right = self.index(
                            self.rowCount() + 1, self.columnCount())
                        self.dataChanged.emit(top_left, bottom_right,
                                              [Qt.DisplayRole])
                        self.layoutChanged.emit()
                        return True
            else:
                if field == TaskColumn.Task and value:
                    # insert only when task name is not empty
                    if self.create_task(value):
                        self.__cache_data()

                        self.layoutAboutToBeChanged.emit()

                        top_left = self.index(0, 0)
                        bottom_right = self.index(
                            self.rowCount() + 1, self.columnCount())
                        self.dataChanged.emit(
                            top_left, bottom_right, [Qt.DisplayRole])

                        self.layoutChanged.emit()

                        return True

        return False

    def headerData(self, section, orientation, role=None):
        """Return the header data.

        Return the data for the given role and section in the header with
        the specified orientation.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return TaskColumn(section).name.replace('_', ' ')
        return QVariant()

    def flags(self, index):
        """Return the item flags for the given index."""
        return Qt.ItemIsEditable | super().flags(index)

    @staticmethod
    def update_task(id_, field, value):
        """Update task field with a given value for a given id."""
        logger = logging.getLogger(__name__)
        args = dict()

        if field == TaskColumn.Task:
            args['name'] = value
        elif field == TaskColumn.Start_Time:
            args['start_time'] = '{:02d}:{:02d}'.format(
                value.hour(), value.minute())
        elif field == TaskColumn.End_Time:
            args['end_time'] = '{:02d}:{:02d}'.format(
                value.hour(), value.minute())

        if args:
            try:
                query = Task.update(**args).where(Task.id == id_)
                logger.debug('Executing query: %s', query.sql())
                return query.execute() > 0
            except IntegrityError:
                return False

        return False

    @staticmethod
    def delete_task(id_):
        """Delete a task with the given id."""
        logger = logging.getLogger(__name__)
        query = Task.delete().where(Task.id == id_)
        logger.debug('Executing query: %s', query.sql())
        return query.execute() > 0

    def create_task(self, task_name):
        """Create a task for a given task name."""
        try:
            query = Task.insert(name=task_name, day=self._day)
            self.logger.debug('Executing query: %s', query.sql())
            # pylint: disable=locally-disabled,E1120
            return query.execute() > 0
        except IntegrityError:
            return False

    @property
    def last_task_cell_index(self):
        """Get the QModelIndex of the last task cell."""
        return self.index(self.rowCount() - 1, TaskColumn.Task.value)

    @property
    def minutes_of_day(self):
        """Get the total time in minutes of today's tasks."""
        minutes = (Task.select(fn.SUM((fn.strftime('%s', Task.end_time)
                                       - fn.strftime('%s', Task.start_time))
                                      .cast('real') / 60).alias('sum')
                               )
                   .where((Task.day == self._day)
                          & Task.start_time.is_null(False)
                          & Task.end_time.is_null(False)
                          )
                   .scalar())
        self.logger.debug('Minutes of day: %s', minutes)
        return minutes or 0

    def __overlaps_other_range(self, task_id, field, value):
        """Check range overlaps another range."""
        if not self._cached_data:
            return False

        start_time = None
        end_time = None
        # find start and end times of task_id.
        for r in self._cached_data:
            if self._cached_data[r][TaskColumn.Id] == task_id:
                if field == TaskColumn.Start_Time:
                    start_time = value
                    end_time = self._cached_data[r][TaskColumn.End_Time]
                if field == TaskColumn.End_Time:
                    start_time = self._cached_data[r][TaskColumn.Start_Time]
                    end_time = value
                break

        # check new value is not in another range and current range does not
        # overlap another start or end time.
        for r in self._cached_data:
            if self._cached_data[r][TaskColumn.Id] != task_id:

                if (self._cached_data[r][TaskColumn.Start_Time]
                        and self._cached_data[r][TaskColumn.End_Time]):

                    if (self._cached_data[r][TaskColumn.Start_Time] < value
                            < self._cached_data[r][TaskColumn.End_Time]):
                        return True

                    if (start_time and end_time
                        and (start_time
                             < self._cached_data[r][TaskColumn.Start_Time]
                             < end_time
                             or start_time
                             < self._cached_data[r][TaskColumn.End_Time]
                             < end_time)):
                        return True

        return False
