#     Copyright (C) 2022  Matthieu PETIOT
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

"""Task counter version database model."""
from datetime import datetime

from peewee import IntegerField, DateTimeField

from taskcounter.db.model import BaseModel


class Version(BaseModel):
    """Version model."""

    version = IntegerField(null=False, unique=True)
    datetime = DateTimeField(null=False, default=datetime.now)

    def __str__(self):
        """Get string representation."""
        return 'Version {} updated {}'.format(self.version, self.datetime)
