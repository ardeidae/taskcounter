""""Tasks counter database model."""

from peewee import (SqliteDatabase, Model, IntegerField, DateField,
                    TimeField, CharField, ForeignKeyField,
                    Check, IntegrityError)


IntegrityError = IntegrityError


DB = SqliteDatabase('database.db')


class MyBaseModel(Model):
    """Base for model classes."""

    class Meta:
        database = DB


class Week(MyBaseModel):
    """Week model."""

    year = IntegerField()
    week_number = IntegerField()
    week_hours = IntegerField(null=True)

    class Meta:
        indexes = (
            (('year', 'week_number'), True),
        )
        order_by = ('year', 'week_number')

    def __str__(self):
        """Get string representation."""
        return 'Week: {}/{}:{}h'.format(self.year, self.week_number,
                                        self.week_hours)


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
