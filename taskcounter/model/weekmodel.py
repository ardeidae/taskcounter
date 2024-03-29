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

import logging

from taskcounter.db import SQL, Day, Task, Week, fn
from taskcounter.enum import ResultColumn, WeekDay
from taskcounter.model import DayModel, SettingModel
from taskcounter.utility import seven_days_of_week, weekday_from_date


class WeekModel:
    """Wrapper for the week model."""

    def __init__(self, year, week_number, parent=None):
        """Construct a week wrapper object."""
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        # get the default work time, to use it as this week value
        default_time = SettingModel.default_week_time()
        self.logger.info('Default time for new week: %s', default_time)
        self._week = Week.get_or_create(year=year,
                                        week_number=week_number,
                                        defaults={'minutes_to_work':
                                                  default_time})[0]
        self.logger.debug('Week: %s', self._week)
        self.__create_days()

    @property
    def minutes_to_work(self):
        """Get work time in minutes of this week instance."""
        minutes = self._week.minutes_to_work
        self.logger.debug('Get minutes to work: %s', minutes)
        return minutes

    @minutes_to_work.setter
    def minutes_to_work(self, minutes_to_work):
        """Set work time in minutes of this week instance."""
        self.logger.debug('Set minutes to work: %s', minutes_to_work)
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
                    day_model = DayModel(day.date, day.week, self.parent)
                    self.logger.debug('Get day model: %s', day_model)
                    return day_model
        return None

    def __create_days(self):
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
        self.logger.debug('Get minutes of week: %s', minutes)
        return minutes or 0

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
        self.logger.debug('Get total minutes to work: %s', minutes)
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
        self.logger.debug('Get total time worked: %s', minutes)
        return minutes or 0

    def week_summary(self, man_day_minutes):
        """Get the week summary: tasks and total time in minutes."""
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

        tasks = self.__summary_from_query(man_day_minutes, query)
        self.logger.debug('Week summary: %s', tasks)
        return tasks

    def daily_summary(self, today_date, man_day_minutes):
        """Get the day summary: tasks and total time in minutes."""
        query = (Task.select(Task.name,
                             fn.SUM((fn.strftime('%s', Task.end_time) -
                                     fn.strftime('%s', Task.start_time))
                                    .cast('real') / 60).alias('sum')
                             )
                 .join(Day)
                 .where((Day.date == today_date)
                        & Task.start_time.is_null(False)
                        & Task.end_time.is_null(False)
                        )
                 .group_by(Task.name)
                 .order_by(SQL('sum').desc()))

        tasks = self.__summary_from_query(man_day_minutes, query)
        self.logger.debug('Daily summary: %s', tasks)
        return tasks

    @staticmethod
    def __summary_from_query(man_day_minutes, query):
        """Return the summary (tasks and total time in minutes) from an
        executed query."""
        tasks = {}
        for counter, row in enumerate(query):
            task = {ResultColumn.Task: row.name, ResultColumn.Time: row.sum,
                    ResultColumn.Decimal_Time: row.sum}
            if man_day_minutes:
                task[ResultColumn.Man_Day] = round(row.sum /
                                                   man_day_minutes, 2)
            else:
                task[ResultColumn.Man_Day] = ''
            tasks[counter] = task
        return tasks
