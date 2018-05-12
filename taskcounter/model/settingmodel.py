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

"""Task counter setting model."""


import pickle

from PyQt5.QtCore import QTime
from PyQt5.QtGui import QColor

from taskcounter.db import IntegrityError, Setting


class SettingModel:
    """Wrapper for the setting model."""

    WEEK_TIME_PROPERTY = 'default_week_time'
    MAN_DAY_TIME_PROPERTY = 'default_man_day_time'
    INVALID_COLOR_PROPERTY = 'invalid_color'
    VALID_COLOR_PROPERTY = 'valid_color'
    CURRENT_CELL_COLOR_PROPERTY = 'current_cell_color'

    @staticmethod
    def insert_or_update(name, value):
        """Insert or update a value for a named setting."""
        dump = pickle.dumps(value).hex()
        try:
            Setting.create(name=name, value=dump)
        except IntegrityError:
            query = Setting.update(value=dump).where(Setting.name == name)
            print('>>> query: ' + str(query.sql()))
            query.execute()

    @staticmethod
    def get_value(name):
        """Get value for a named setting."""
        value = None
        hex_value = (Setting.select(Setting.value)
                            .where(Setting.name == name)
                            .scalar())
        if hex_value:
            try:
                bytes_value = bytes.fromhex(hex_value)
                value = pickle.loads(bytes_value)
            except (pickle.PickleError, ValueError):
                print('>>> Error when reading setting {}'.format(name))

        return value

    @classmethod
    def default_week_time(cls):
        """Get the default week time."""
        return cls.get_value(cls.WEEK_TIME_PROPERTY) or (35 * 60)

    @classmethod
    def set_default_week_time(cls, default_week_time):
        """Set the default week time."""
        cls.insert_or_update(cls.WEEK_TIME_PROPERTY,
                             default_week_time)

    @classmethod
    def default_man_day_time(cls):
        """Get the default man day time."""
        return cls.get_value(cls.MAN_DAY_TIME_PROPERTY) or QTime(7, 0)

    @classmethod
    def set_default_man_day_time(cls, default_man_day_time):
        """Set the default man day time."""
        cls.insert_or_update(cls.MAN_DAY_TIME_PROPERTY,
                             default_man_day_time)

    @classmethod
    def invalid_color(cls):
        """Get the invalid color setting."""
        return (cls.get_value(cls.INVALID_COLOR_PROPERTY) or
                QColor('#FFCDD2'))

    @classmethod
    def set_invalid_color(cls, invalid_color):
        """Set the invalid color setting."""
        cls.insert_or_update(cls.INVALID_COLOR_PROPERTY, invalid_color)

    @classmethod
    def valid_color(cls):
        """Get the valid color setting."""
        return (cls.get_value(cls.VALID_COLOR_PROPERTY) or
                QColor('#DAF7A6'))

    @classmethod
    def set_valid_color(cls, valid_color):
        """Set the valid color setting."""
        cls.insert_or_update(cls.VALID_COLOR_PROPERTY, valid_color)

    @classmethod
    def current_cell_color(cls):
        """Get the current cell color setting."""
        return (cls.get_value(cls.CURRENT_CELL_COLOR_PROPERTY) or
                QColor('#fffd88'))

    @classmethod
    def set_current_cell_color(cls, current_cell_color):
        """Set the current cell color setting."""
        cls.insert_or_update(cls.CURRENT_CELL_COLOR_PROPERTY,
                             current_cell_color)
