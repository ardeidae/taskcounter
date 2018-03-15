"""Tasks counter model."""

from datetime import date, time, timedelta
from enum import Enum, unique

from PyQt5.QtCore import QAbstractTableModel, Qt, QTime, QVariant
from PyQt5.QtGui import QBrush, QColor

from database import Day, IntegrityError, Task, Week, fn


@unique
class WeekDay(Enum):
    """Week day name Enum."""

    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6


@unique
class Column(Enum):
    """Columns Enum."""

    Id = 0
    Task = 1
    Start_Time = 2
    End_Time = 3


def weekday_from_date(date_):
    """From a date, returns a WeekDay."""
    if isinstance(date_, date):
        return WeekDay(date_.weekday())
    return None


def weeks_for_year(year):
    """From a year, gets the number of iso weeks."""
    # https://stackoverflow.com/a/29263010
    try:
        last_week = date(int(year), 12, 28)
    except ValueError:
        return None
    else:
        return last_week.isocalendar()[1]
    return None


def seven_days_of_week(a_year, a_week_number):
    """Gets seven dates from a given year and a given week number."""

    try:
        year = int(a_year)
        week_number = int(a_week_number)
    except ValueError:
        return None
    else:
        if weeks_for_year(year) < week_number or week_number < 1:
            return None

        # december 28 is always in the last week ot the year.
        december_28 = date(year - 1, 12, 28)

        monday_of_first_week = december_28

        # go until next monday (first week of the year)
        while 'the next monday has not been found yet':
            monday_of_first_week += timedelta(days=1)
            if monday_of_first_week.weekday() == WeekDay.Monday.value:
                break
        # now monday_of_first_week is really the monday of the first week

        assert(monday_of_first_week.weekday() == WeekDay.Monday.value)

        # add week_number - 1 to find the monday of the week_number th week
        searched_week = monday_of_first_week + \
            timedelta(weeks=(week_number - 1))

        for i in range(7):
            yield searched_week + timedelta(days=i)


class WeekWrapper:
    """Wrapper for the week model."""

    def __init__(self, year, week_number):
        """Constructs a week wrapper object."""
        self._week = Week.get_or_create(year=year,
                                        week_number=week_number)[0]
        self.__create_days__()

    @property
    def week_hours(self):
        """Gets hours of this week instance."""
        return self._week.week_hours

    @week_hours.setter
    def week_hours(self, week_hours):
        """Sets hours of this week instance."""
        self._week.week_hours = week_hours
        self._week.save()

    def __getitem__(self, week_day):
        """
        Gets item with bracket operator. Takes a WeekDay value.

        Returns a DayWrapper.
        """
        if week_day in WeekDay:
            for day in (Day.select(Day)
                        .join(Week)
                        .where((Week.week_number == self._week.week_number) &
                               (Week.year == self._week.year))
                        .order_by(Day.date)):
                if week_day is weekday_from_date(day.date):
                    return DayWrapper(day.date, day.week)
        return None

    def __create_days__(self):
        """Creates the days of this week."""
        for date_ in seven_days_of_week(self._week.year,
                                        self._week.week_number):
            DayWrapper(date_=date_, week=self._week)

    @property
    def minutes_of_week(self):
        """Gets the total time in minutes of week's tasks."""
        minutes = (Task.select(fn.SUM((fn.strftime('%s', Task.end_time)
                                       - fn.strftime('%s', Task.start_time))
                                      .cast('real') / 60).alias('sum')
                               ).join(Day)
                   .where((Day.week == self._week)
                          & Task.start_time.is_null(False)
                          & Task.end_time.is_null(False)
                          )
                   .scalar())
        return minutes or 0


class DayWrapper(QAbstractTableModel):
    """Wrapper for the day model."""

    def __init__(self, date_, week):
        """Constructs a day wrapper object."""
        super().__init__()
        self._day = Day.get_or_create(date=date_,
                                      week=week)[0]
        self.data = None
        self.__cache_data__()

    @property
    def week(self):
        """Gets the week property."""
        return self._day.week

    @property
    def date(self):
        """Gets the date property."""
        return self._day.date

    def rowCount(self, parent=None):
        """Returns the number of rows under the given parent."""
        return len(self.data) + 1

    def columnCount(self, parent=None):
        """Returns the number of columns for the children of the given parent."""
        return 4

    def __cache_data__(self):
        """Caches data."""
        self.data = {}
        for counter, task in enumerate(Task.select(Task.id, Task.name,
                                                   Task.start_time,
                                                   Task.end_time)
                                       .join(Day)
                                       .where(Task.day == self._day)
                                       .order_by(Task.id)):
            row = {}
            row[Column.Id] = task.id
            row[Column.Task] = task.name
            row[Column.Start_Time] = task.start_time
            row[Column.End_Time] = task.end_time
            self.data[counter] = row

    def data(self, index, role):
        """Returns the data stored under the given role for the item referred
        to by the index."""
        if not index.isValid():
            return QVariant()

        row = index.row()
        column = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            try:
                value = self.data[row][Column(column)]
            except KeyError:
                return QVariant()
            else:
                if column == Column.Id.value:
                    return int(value)
                elif column == Column.Task.value:
                    return str(value)
                elif column in (Column.Start_Time.value,
                                Column.End_Time.value):
                    try:
                        a_time = QTime(value.hour, value.minute, value.second)
                        return QVariant(a_time)
                    except AttributeError:
                        if role == Qt.EditRole:
                            return QVariant(QTime(0, 0))
                        else:
                            return QVariant()
        elif role == Qt.FontRole:
            pass
        elif role == Qt.BackgroundRole:
            try:
                start = self.data[row][Column.Start_Time]
                end = self.data[row][Column.End_Time]
                red_brush = QBrush(QColor('#FFCDD2'))
                if not start or not end:
                    return red_brush
                if start >= end:
                    return red_brush
                return QBrush(QColor('#DAF7A6'))
            except KeyError:
                pass

        elif role == Qt.TextAlignmentRole:
            if column == Column.Task.value:
                return Qt.AlignLeft | Qt.AlignVCenter
            else:
                return Qt.AlignCenter | Qt.AlignVCenter

        return QVariant()

    def setData(self, index, value, role):
        """Sets the role data for the item at index to value."""
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()

            field = Column(column)

            if row in self.data:
                task_id = self.data[row][Column.Id]

                if field == Column.Task and not value:
                    if self.delete_task(task_id):
                        self.__cache_data__()
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

                    if field == Column.Start_Time:
                        end = self.data[row][Column.End_Time]
                        if end and value >= end:
                            return False
                    elif field == Column.End_Time:
                        start = self.data[row][Column.Start_Time]
                        if start and value <= start:
                            return False

                    if self.update_task(task_id, field, value):
                        self.__cache_data__()

                        self.layoutAboutToBeChanged.emit()
                        top_left = self.index(0, 0)
                        bottom_right = self.index(
                            self.rowCount() + 1, self.columnCount())
                        self.dataChanged.emit(top_left, bottom_right,
                                              [Qt.DisplayRole])
                        self.layoutChanged.emit()
                        return True
            else:
                if field == Column.Task and value:
                    # insert only when task name is not empty
                    if self.create_task(value):
                        self.__cache_data__()

                        self.layoutAboutToBeChanged.emit()

                        top_left = self.index(0, 0)
                        bottom_right = self.index(
                            self.rowCount() + 1, self.columnCount())
                        self.dataChanged.emit(
                            top_left, bottom_right, [Qt.DisplayRole])

                        self.layoutChanged.emit()

                        return True

        return False

    def headerData(self, section, orientation, role):
        """Returns the data for the given role and section in the header with
        the specified orientation."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return Column(section).name.replace('_', ' ')
        return QVariant()

    def flags(self, index):
        """Returns the item flags for the given index."""
        return Qt.ItemIsEditable | super().flags(index)

    @staticmethod
    def update_task(id, field, value):
        """Updates task field with a given value for a given id."""
        args = dict()

        if field == Column.Task:
            args['name'] = value
        elif field == Column.Start_Time:
            args['start_time'] = '{:02d}:{:02d}'.format(
                value.hour(), value.minute())
        elif field == Column.End_Time:
            args['end_time'] = '{:02d}:{:02d}'.format(
                value.hour(), value.minute())

        if args:
            try:
                query = Task.update(**args).where(Task.id == id)
                print('>>> query: ' + str(query.sql()))
                return query.execute() > 0
            except IntegrityError:
                return False

        return False

    @staticmethod
    def delete_task(id):
        """Deletes a task with the given id."""
        query = Task.delete().where(Task.id == id)
        print('>>> query: ' + str(query.sql()))
        return query.execute() > 0

    def create_task(self, task_name):
        """Creates a task for a given task name."""

        try:
            query = Task.insert(name=task_name, day=self._day)
            print('>>> query: ' + str(query.sql()))
            if query.execute() > 0:
                return True
        except IntegrityError:
            return False

    @property
    def last_task_cell_index(self):
        """Gets the QModelIndex of the last task cell."""

        return self.index(self.rowCount() - 1, Column.Task.value)

    @property
    def minutes_of_day(self):
        """Gets the total time in minutes of today's tasks."""
        minutes = (Task.select(fn.SUM((fn.strftime('%s', Task.end_time)
                                       - fn.strftime('%s', Task.start_time))
                                      .cast('real') / 60).alias('sum')
                               )
                   .where((Task.day == self._day)
                          & Task.start_time.is_null(False)
                          & Task.end_time.is_null(False)
                          )
                   .scalar())
        return minutes or 0

def get_last_unique_task_names():
    """Returns the last unique task names since last three months."""
    last_3_months = date.today() + timedelta(days=-90)
    return (tuple(x.name for x in Task.select(Task.name)
                  .join(Day)
                  .distinct()
                  .where(Day.date > last_3_months)
                  .order_by(Task.name)))
