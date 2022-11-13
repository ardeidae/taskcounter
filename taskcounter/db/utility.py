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
import sys

from .model import DB
from .day import Day
from .setting import Setting
from .task import Task, TaskOld
from .version import Version
from .week import Week
from ..model.versionmodel import VersionModel


def create_database():
    """Create the database."""
    logger = logging.getLogger(__name__)
    logger.info('Connect to database')
    DB.connect()
    logger.info('Create tables Week, Day, Task, Setting if necessary')
    DB.create_tables([Week, Day, TaskOld, Setting], safe=True)


def migrate_database():
    """Migrate database to the last version."""
    logger = logging.getLogger(__name__)

    # add Version table
    logger.info('Create table Version')
    DB.create_tables([Version], safe=True)

    logger.info('Check migrations')
    current_version = VersionModel.get_current_version()
    if current_version is None:
        if migrate_to_version_1():
            next_version = 1
            update_ok = VersionModel.set_current_version(next_version)
            if update_ok:
                logger.info('Database migrated to version: %s', next_version)
            else:
                logger.error('Unable to migrate database to version: %s', next_version)
                sys.exit(1)


def migrate_to_version_1():
    """We need to change the check constraint. We must delete and create the
    table again"""
    logger = logging.getLogger(__name__)
    logger.info('Migrate to version 1')

    logger.info('Get old task entries')
    task_list = []
    for record in TaskOld.select():
        task = {
            'id': record.id,
            'name': record.name,
            'start_time': record.start_time,
            'end_time': record.end_time,
            'day_id': record.day_id,
        }
        task_list.append(task)

    logger.info('Drop table task')
    DB.drop_tables([TaskOld])

    logger.info('Create new table task')
    DB.create_tables([Task], safe=True)

    logger.info('Insert entries in new table task')
    for task in task_list:
        Task.create(
            id=task['id'],
            name=task['name'],
            start_time=task['start_time'],
            end_time=task['end_time'],
            day_id=task['day_id'],
        )

    return True


def close_database():
    """Close the database."""
    logger = logging.getLogger(__name__)
    logger.info('Close database')
    DB.close()
