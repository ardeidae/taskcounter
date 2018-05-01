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

"""Task counter week model."""


from taskcounter.db import SQL, Day, Task, Week, fn
from taskcounter.enum import ResultColumn, WeekDay
from taskcounter.model import DayModel
from taskcounter.utility import seven_days_of_week, weekday_from_date


class WeekModel:
    """Wrapper for the week model."""

    def __init__(self, year, week_number, parent=None):
        """Construct a week wrapper object."""
        self.parent = parent
        # get the last work time entered, to use it a default value
        last_time = self.__last_work_time_entered__()
        self._week = Week.get_or_create(year=year,
                                        week_number=week_number,
                                        defaults={'minutes_to_work':
                                                  last_time})[0]
        self.__create_days__()

    @property
    def minutes_to_work(self):
        """Get work time in minutes of this week instance."""
        return self._week.minutes_to_work

    @minutes_to_work.setter
    def minutes_to_work(self, minutes_to_work):
        """Set work time in minutes of this week instance."""
        self._week.minutes_to_work = minutes_to_work
        self._week.save()

    def __getitem__(self, week_day):
        """
        Get item with bracket operator. Take a WeekDay value.

        Return a DayModel.
        """
        if week_day in WeekDay:
            for day in (Day.select(Day)
                        .join(Week)
                        .where((Week.week_number == self._week.week_number) &
                               (Week.year == self._week.year))
                        .order_by(Day.date)):
                if week_day is weekday_from_date(day.date):
                    return DayModel(day.date, day.week, self.parent)
        return None

    def __create_days__(self):
        """Create the days of this week."""
        for date_ in seven_days_of_week(self._week.year,
                                        self._week.week_number):
            DayModel(date_, self._week, self.parent)

    @property
    def minutes_of_week(self):
        """Get the total time in minutes of week's tasks."""
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

    def __last_work_time_entered__(self):
        """Get the last work time entered, the newest."""
        return (Week.select(Week.minutes_to_work)
                    .where(Week.minutes_to_work.is_null(False))
                    .order_by(-Week.year, -Week.week_number)
                    .scalar()) or 0

    @property
    def total_time_to_work(self):
        """Get the total time (minutes) to work for the entire period."""
        # we ignore time of weeks that do not have tasks.
        minutes = (Week.select(fn.SUM(Week.minutes_to_work))
                       .where(Week.id
                              .in_(Week.select(Week.id).distinct()
                                   .join(Day).join(Task)
                                   .where(Task.start_time.is_null(False) &
                                          Task.end_time.is_null(False))))
                   .scalar())
        return minutes or 0

    @property
    def total_time_worked(self):
        """Get the total worked time (minutes) for the entire period."""
        minutes = (Task.select(fn.SUM((fn.strftime('%s', Task.end_time)
                                       - fn.strftime('%s', Task.start_time))
                                      .cast('real') / 60).alias('sum')
                               )
                   .where(Task.start_time.is_null(False)
                          & Task.end_time.is_null(False)
                          )
                   .scalar())
        return minutes or 0

    def week_summary(self, manday_minutes):
        """Get the week summary: tasks and total time in minutes."""
        tasks = {}
        query = (Task.select(Task.name,
                             fn.SUM((fn.strftime('%s', Task.end_time) -
                                     fn.strftime('%s', Task.start_time))
                                    .cast('real') / 60).alias('sum')
                             )
                 .join(Day)
                 .where((Day.week == self._week)
                        & Task.start_time.is_null(False)
                        & Task.end_time.is_null(False)
                        )
                 .group_by(Task.name)
                 .order_by(SQL('sum').desc()))

        for counter, row in enumerate(query):
            task = {}
            task[ResultColumn.Task] = row.name
            task[ResultColumn.Time] = row.sum
            if manday_minutes:
                task[ResultColumn.Man_Day] = round(row.sum /
                                                   manday_minutes, 2)
            else:
                task[ResultColumn.Man_Day] = ''
            tasks[counter] = task

        return tasks
