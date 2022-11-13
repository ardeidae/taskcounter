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

"""Task counter base database model."""

from os import path

from peewee import Model, SqliteDatabase

from taskcounter import taskcounter_dir

DB = SqliteDatabase(path.join(taskcounter_dir, 'taskcounter.db'))


class BaseModel(Model):
    """Base for model classes."""

    class Meta:
        """Meta class."""

        database = DB
