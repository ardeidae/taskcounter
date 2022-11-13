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

"""Task counter version model."""

import logging

from peewee import IntegrityError

from taskcounter.db import fn, Version


class VersionModel:
    """Wrapper for the version model."""

    @staticmethod
    def get_current_version():
        logger = logging.getLogger(__name__)
        max_version = Version.select(fn.MAX(Version.version)).scalar()
        logger.info('Get last db version: %s', max_version)
        return max_version

    @staticmethod
    def set_current_version(version):
        logger = logging.getLogger(__name__)
        try:
            version = int(version)
        except ValueError:
            logging.error('Unable to convert %s to int', version)
            return False
        else:
            try:
                Version.create(version=version)
            except IntegrityError:
                logger.error('Unable to create version: %s', version)
                return False
            else:
                logger.info('Added version: %s', version)
                return True
