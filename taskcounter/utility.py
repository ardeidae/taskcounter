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

"""Task counter utility functions."""

import re
from datetime import date, timedelta

from taskcounter.enum import WeekDay


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
    except (TypeError, ValueError):
        return None
    else:
        return last_week.isocalendar()[1]


def seven_days_of_week(a_year, a_week_number):
    """Get seven dates from a given year and a given week number."""
    try:
        year = int(a_year)
        week_number = int(a_week_number)
    except (TypeError, ValueError):
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


def minutes_to_time(a_total_minutes):
    """Get a tuple hours / minutes from a number of minutes."""
    try:
        total_minutes = int(a_total_minutes)
    except (TypeError, ValueError):
        return None
    else:
        if total_minutes < 0:
            return None
        else:
            return divmod(total_minutes, 60)


def minutes_to_time_str(a_total_minutes):
    """Get a hh:mm string from a number of minutes."""
    time = minutes_to_time(a_total_minutes)
    if time:
        return '{:02d}:{:02d}'.format(*time)
    return None


def split_color(color):
    """Split hex color like #rrggbb or #rgb into three int components."""
    color = color[1:]
    r = g = b = 0
    if len(color) == 6:
        r, g, b = [int(color[i:i + 2], 16) for i in range(0, 6, 2)]
    elif len(color) == 3:
        r, g, b = [int(color[i:i + 1], 16) for i in range(0, 3)]
    return r, g, b


def color_between(start_color, end_color, percent):
    """Get a hex color between a start and end color using a percentage."""
    if percent < 0:
        percent = 0
    if percent > 1:
        percent = 1

    regexp = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    if (re.search(regexp, start_color)
            and re.search(regexp, end_color)):

        r1, g1, b1 = split_color(start_color)
        r2, g2, b2 = split_color(end_color)

        return ('#{:02x}{:02x}{:02x}'.format(int(r1 + (r2 - r1) * percent),
                                             int(g1 + (g2 - g1) * percent),
                                             int(b1 + (b2 - b1) * percent)))

    else:
        return '#000000'


def contrast_color(color):
    """Get black or white contrast depending on a given color."""
    regexp = r'^#(?:[0-9a-fA-F]{3}){1,2}$'

    if re.search(regexp, color):
        r, g, b = split_color(color)
        lightness = r * 0.299 + g * 0.587 + b * 0.114
        return '#000000' if lightness > 160 else '#ffffff'
    else:
        return '#000000'
