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

"""Task counter day database model."""

from peewee import DateField, ForeignKeyField

from .model import BaseModel
from .week import Week


class Day(BaseModel):
    """Day model."""

    date = DateField(unique=True)
    week = ForeignKeyField(Week, related_name='days')

    def __str__(self):
        """Get string representation."""
        return 'Day: {}'.format(self.date)
