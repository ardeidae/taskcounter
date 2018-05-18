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

"""Task counter root module init."""

import os
import logging
from logging.handlers import RotatingFileHandler

taskcounter_dir = os.path.join(os.path.expanduser('~'),
                               '.taskcounter')

log_dir = os.path.join(taskcounter_dir, 'log')

log_file = os.path.join(log_dir, 'taskcounter.log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M')

rotate_handler = RotatingFileHandler(filename=log_file, mode='a',
                                     backupCount=9, maxBytes=1000000,
                                     encoding='utf-8')

rotate_handler.setFormatter(formatter)
rotate_handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(rotate_handler)
logger.info('Initialize logger')
