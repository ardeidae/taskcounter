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

"""Task counter model utility functions."""

import logging

from datetime import date, timedelta

from taskcounter.db import Day, Task


def get_last_unique_task_names():
    """Return the last unique task names since last three months."""
    logger = logging.getLogger(__name__)

    last_3_months = date.today() + timedelta(days=-90)
    logger.debug('Last unique task names period: %s', last_3_months)
    tasks = (tuple(x.name for x in Task.select(Task.name)
                   .join(Day)
                   .distinct()
                   .where(Day.date > last_3_months)
                   .order_by(Task.name)))
    logger.debug('Last unique task names: %s', tasks)
    return tasks
