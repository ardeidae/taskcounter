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

import logging

import re
from datetime import date, timedelta

from taskcounter.enum import WeekDay


def weekday_from_date(date_):
    """From a date, returns a WeekDay."""
    logger = logging.getLogger(__name__)
    if isinstance(date_, date):
        weekday = WeekDay(date_.weekday())
        logger.debug('Week day: %s', weekday)
        return weekday
    logger.error('%s is not an instance of date.', date_)
    return None


def weeks_for_year(year):
    """From a year, gets the number of iso weeks."""
    # https://stackoverflow.com/a/29263010
    logger = logging.getLogger(__name__)
    try:
        last_week = date(int(year), 12, 28)
        logger.debug('Last week: %s', last_week)
    except (TypeError, ValueError):
        logger.error('Unable to convert %s to int.', exc_info=True)
        return None
    else:
        week = last_week.isocalendar()[1]
        logger.debug('ISO calendar week number: %s', week)
        return week


def seven_days_of_week(a_year, a_week_number):
    """Get seven dates from a given year and a given week number."""
    logger = logging.getLogger(__name__)

    try:
        year = int(a_year)
        week_number = int(a_week_number)
        logger.debug('Year: %s, week: %s', year, week_number)
    except (TypeError, ValueError):
        logger.error('Unable to convert %s or %s to int.',
                     a_year, a_week_number, exc_info=True)
        return None
    else:
        if weeks_for_year(year) < week_number or week_number < 1:
            return None

        # december 28 is always in the last week ot the year.
        december_28 = date(year - 1, 12, 28)
        logger.debug('December 28: %s', december_28)

        monday_of_first_week = december_28

        # go until next monday (first week of the year)
        while 'the next monday has not been found yet':
            monday_of_first_week += timedelta(days=1)
            if monday_of_first_week.weekday() == WeekDay.Monday.value:
                break
        # now monday_of_first_week is really the monday of the first week
        logger.debug('Monday of first weel: %s', monday_of_first_week)

        assert(monday_of_first_week.weekday() == WeekDay.Monday.value)

        # add week_number - 1 to find the monday of the week_number th week
        searched_week = monday_of_first_week + \
            timedelta(weeks=(week_number - 1))
        logger.debug('Searched week: %s', searched_week)

        for i in range(7):
            day = searched_week + timedelta(days=i)
            logger.debug('Yield: %s', day)
            yield day


def minutes_to_time(a_total_minutes):
    """Get a tuple hours / minutes from a number of minutes."""
    logger = logging.getLogger(__name__)
    try:
        total_minutes = int(a_total_minutes)
    except (TypeError, ValueError):
        logger.error('Unable to convert %s to int.',
                     a_total_minutes, exc_info=True)
        return None
    else:
        if total_minutes < 0:
            logger.warning('Total minutes less than zero: %s', total_minutes)
            return None
        else:
            time = divmod(total_minutes, 60)
            logger.debug('Time: %s', time)
            return time


def minutes_to_time_str(a_total_minutes):
    """Get a hh:mm string from a number of minutes."""
    logger = logging.getLogger(__name__)
    logger.debug('Total minutes: %s', a_total_minutes)

    time = minutes_to_time(a_total_minutes)

    logger.debug('Time: %s', time)
    if time:
        time = '{:02d}:{:02d}'.format(*time)
        logger.debug('Return: %s', time)
        return time
    logger.error('Return None')
    return None


def split_color(color):
    """Split hex color like #rrggbb or #rgb into three int components."""
    color = color[1:]
    logger = logging.getLogger(__name__)
    logger.debug('Input color to split: %s', color)
    r = g = b = 0
    if len(color) == 6:
        r, g, b = [int(color[i:i + 2], 16) for i in range(0, 6, 2)]
    elif len(color) == 3:
        r, g, b = [int(color[i:i + 1], 16) for i in range(0, 3)]
    logger.debug('Split: %s', (r, g, b))
    return r, g, b


def color_between(start_color, end_color, percent):
    """Get a hex color between a start and end color using a percentage."""
    logger = logging.getLogger(__name__)
    logger.debug('Get color between %s and %s with ratio %s',
                 start_color, end_color, percent)

    if percent < 0:
        percent = 0
    if percent > 1:
        percent = 1

    logger.debug('Retained ratio: %s', percent)

    regexp = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    if (re.search(regexp, start_color)
            and re.search(regexp, end_color)):
        logger.debug('Start and end colors match regexp')

        r1, g1, b1 = split_color(start_color)
        r2, g2, b2 = split_color(end_color)

        logger.debug('Start split color: %s', (r1, g1, b1))
        logger.debug('End split color: %s', (r2, g2, b2))

        color = ('#{:02x}{:02x}{:02x}'.format(int(r1 + (r2 - r1) * percent),
                                              int(g1 + (g2 - g1) * percent),
                                              int(b1 + (b2 - b1) * percent)))

    else:
        logger.warning('Start or end color does not match regexp')
        color = '#000000'

    logger.debug('Color between: %s', color)
    return color


def contrast_color(color):
    """Get black or white contrast depending on a given color."""
    regexp = r'^#(?:[0-9a-fA-F]{3}){1,2}$'

    logger = logging.getLogger(__name__)
    logger.debug('Get constrast color for %s', color)

    if re.search(regexp, color):
        r, g, b = split_color(color)
        logger.debug('Split color: %s', (r, g, b))
        lightness = r * 0.299 + g * 0.587 + b * 0.114
        logger.debug('Lightness: %s', lightness)
        result = '#000000' if lightness > 160 else '#ffffff'
    else:
        result = '#000000'

    logger.debug('Contrast color: %s', result)
    return result
