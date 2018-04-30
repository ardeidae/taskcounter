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

"""Task counter week database model."""

from peewee import IntegerField

from .model import BaseModel


class Week(BaseModel):
    """Week model."""

    year = IntegerField()
    week_number = IntegerField()
    minutes_to_work = IntegerField(default=0)

    class Meta:
        indexes = (
            (('year', 'week_number'), True),
        )
        order_by = ('year', 'week_number')

    def __str__(self):
        """Get string representation."""
        return 'Week: {}/{}:{}h'.format(self.year, self.week_number,
                                        self.minutes_to_work)
