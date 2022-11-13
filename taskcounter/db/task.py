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

"""Task counter task database model."""

from peewee import CharField, Check, ForeignKeyField, TimeField

from .day import Day
from .model import BaseModel


class TaskOld(BaseModel):
    """Task old model."""

    name = CharField()
    start_time = TimeField(null=True)
    end_time = TimeField(null=True)
    day = ForeignKeyField(Day, related_name='tasks')

    class Meta:
        """Meta class."""
        table_name = "task"
        constraints = [Check("start_time is NULL or start_time LIKE '__:__'"),
                       Check("end_time is NULL or end_time LIKE '__:__'")]

    def __str__(self):
        """Get string representation."""
        return 'Task: {} {}/{}'.format(self.name, self.start_time,
                                       self.end_time)


class Task(BaseModel):
    """Task model."""

    name = CharField()
    start_time = TimeField(null=True)
    end_time = TimeField(null=True)
    day = ForeignKeyField(Day, related_name='tasks')

    class Meta:
        """Meta class."""
        table_name = "task"
        constraints = [Check("start_time is NULL or start_time LIKE '__:__:__'"),
                       Check("end_time is NULL or end_time LIKE '__:__:__'")]

    def __str__(self):
        """Get string representation."""
        return 'Task: {} {}/{}'.format(self.name, self.start_time,
                                       self.end_time)
