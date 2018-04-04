#     Copyright (C) 2018  Matthieu PETIOT
#
#     https://github.com/ardeidae/tasks-counter
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

""""Tasks counter database model."""

from peewee import (SQL, CharField, Check, DateField, ForeignKeyField,
                    IntegerField, IntegrityError, Model, SqliteDatabase,
                    TimeField, fn)

IntegrityError = IntegrityError
fn = fn
SQL = SQL


DB = SqliteDatabase('database.db')


class MyBaseModel(Model):
    """Base for model classes."""

    class Meta:
        database = DB


class Week(MyBaseModel):
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


class Day(MyBaseModel):
    """Day model."""

    date = DateField(unique=True)
    week = ForeignKeyField(Week, related_name='days')

    def __str__(self):
        """Get string representation."""
        return 'Day: {}'.format(self.date)


class Task(MyBaseModel):
    """Task Model."""

    name = CharField()
    start_time = TimeField(null=True)
    end_time = TimeField(null=True)
    day = ForeignKeyField(Day, related_name='tasks')

    class Meta:
        constraints = [Check("start_time is NULL or start_time LIKE '__:__'"),
                       Check("end_time is NULL or end_time LIKE '__:__'")]

    def __str__(self):
        """Get string representation."""
        return 'Task: {} {}/{}'.format(self.name, self.start_time,
                                       self.end_time)


def create_database():
    """Create the database."""
    DB.connect()
    DB.create_tables([Week, Day, Task], safe=True)


def close_database():
    """Close the database."""
    DB.close()


if __name__ == '__main__':
    create_database()
