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

from .model import DB
from .day import Day
from .setting import Setting
from .task import Task
from .week import Week


def create_database():
    """Create the database."""
    logger = logging.getLogger(__name__)
    logger.info('Connect to database')
    DB.connect()
    logger.info('Create tables if necessary')
    DB.create_tables([Week, Day, Task, Setting], safe=True)


def close_database():
    """Close the database."""
    logger = logging.getLogger(__name__)
    logger.info('Close database')
    DB.close()
