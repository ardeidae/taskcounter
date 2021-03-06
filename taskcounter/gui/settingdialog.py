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

"""Task counter setting dialog."""

import logging

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QColorDialog, QDialog, QGridLayout, QLabel,
                             QPushButton, QTimeEdit)

from taskcounter.gui import CenterMixin, DurationEdit
from taskcounter.model import SettingModel
from taskcounter.utility import contrast_color


class SettingDialog(CenterMixin, QDialog):
    """Settings dialog."""

    def __init__(self, parent=None):
        """Construct a settings dialog."""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Opening setting dialog')
        self.setWindowTitle(self.tr('Edit preferences'))
        self.center()

        self.invalid_color = None
        self.valid_color = None
        self.current_cell_color = None

        self.__update_colors()

        week_time_label = QLabel(self.tr('Default week time'), self)
        self.week_time = DurationEdit(parent=self, hour_length=2)
        self.week_time.minutes = SettingModel.default_week_time()
        self.logger.info('Read default week time minutes: %s',
                         SettingModel.default_week_time())
        self.week_time.valueChanged.connect(self.__week_time_changed)

        man_day_time_label = QLabel(self.tr('Default man day time'), self)
        self.man_day_time = QTimeEdit(
            SettingModel.default_man_day_time(), self)
        self.logger.info('Read default man day time: %s',
                         SettingModel.default_man_day_time()
                                     .toString('hh:mm'))
        self.man_day_time.timeChanged.connect(
            self.__man_day_time_changed)

        invalid_color_label = QLabel(self.tr('Invalid color'), self)
        self.invalid_color_button = QPushButton(self.tr('Text'), self)
        self.invalid_color_button.clicked.connect(
            self.__open_invalid_color_dialog)

        valid_color_label = QLabel(self.tr('Valid color'), self)
        self.valid_color_button = QPushButton(self.tr('Text'), self)
        self.valid_color_button.clicked.connect(
            self.__open_valid_color_dialog)

        current_cell_color_label = QLabel(self.tr('Current cell color'), self)
        self.current_cell_color_button = QPushButton(self.tr('Text'), self)
        self.current_cell_color_button.clicked.connect(
            self.__open_current_cell_color_dialog)

        self.__update_buttons_colors()

        main_layout = QGridLayout()

        main_layout.addWidget(week_time_label, 0, 0)
        main_layout.addWidget(self.week_time, 0, 1)

        main_layout.addWidget(man_day_time_label, 1, 0)
        main_layout.addWidget(self.man_day_time, 1, 1)

        main_layout.addWidget(invalid_color_label, 2, 0)
        main_layout.addWidget(self.invalid_color_button, 2, 1)

        main_layout.addWidget(valid_color_label, 3, 0)
        main_layout.addWidget(self.valid_color_button, 3, 1)

        main_layout.addWidget(current_cell_color_label, 4, 0)
        main_layout.addWidget(self.current_cell_color_button, 4, 1)

        self.setLayout(main_layout)

    @pyqtSlot()
    def __week_time_changed(self):
        """Update the week time setting."""
        SettingModel.set_default_week_time(self.week_time.minutes)
        self.logger.info('Write default week time minutes: %s',
                         self.week_time.minutes)

    @pyqtSlot()
    def __man_day_time_changed(self):
        """Update the man day time setting."""
        SettingModel.set_default_man_day_time(self.man_day_time.time())
        self.logger.info('Write default man day time: %s',
                         self.man_day_time.time().toString('hh:mm'))

    @pyqtSlot()
    def __open_invalid_color_dialog(self):
        """Update the invalid color setting."""
        color = QColorDialog.getColor(self.invalid_color, self,
                                      self.tr('Select invalid color'),
                                      QColorDialog.DontUseNativeDialog)
        if color.isValid():
            SettingModel.set_invalid_color(color)
            self.logger.info('Write invalid color: %s',
                             color.name())

        self.__update_colors()
        self.__update_buttons_colors()

    @pyqtSlot()
    def __open_valid_color_dialog(self):
        """Update the valid color setting."""
        color = QColorDialog.getColor(self.valid_color, self,
                                      self.tr('Select invalid color'),
                                      QColorDialog.DontUseNativeDialog)
        if color.isValid():
            SettingModel.set_valid_color(color)
            self.logger.info('Write valid color: %s',
                             color.name())

        self.__update_colors()
        self.__update_buttons_colors()

    @pyqtSlot()
    def __open_current_cell_color_dialog(self):
        """Update the current cell color setting."""
        color = QColorDialog.getColor(self.current_cell_color, self,
                                      self.tr('Select current cell color'),
                                      QColorDialog.DontUseNativeDialog)
        if color.isValid():
            SettingModel.set_current_cell_color(color)
            self.logger.info('Write current cell color: %s',
                             color.name())

        self.__update_colors()
        self.__update_buttons_colors()

    def __update_colors(self):
        """Update the local colors values."""
        self.invalid_color = SettingModel.invalid_color()
        self.valid_color = SettingModel.valid_color()
        self.current_cell_color = SettingModel.current_cell_color()
        self.logger.info('Read invalid color: %s',
                         self.invalid_color.name())
        self.logger.info('Read valid color: %s',
                         self.valid_color.name())
        self.logger.info('Read current cell color: %s',
                         self.current_cell_color.name())

    def __update_buttons_colors(self):
        """Update the buttons colors."""
        invalid_color = self.invalid_color.name()
        invalid_color_contrast = contrast_color(invalid_color)
        invalid_style = ('background-color:{}; color:{};'
                         .format(invalid_color, invalid_color_contrast)
                         )
        self.invalid_color_button.setStyleSheet(invalid_style)

        valid_color = self.valid_color.name()
        valid_color_contrast = contrast_color(valid_color)
        valid_style = ('background-color:{}; color:{};'
                       .format(valid_color, valid_color_contrast)
                       )
        self.valid_color_button.setStyleSheet(valid_style)

        current_cell_color = self.current_cell_color.name()
        current_cell_color_contrast = contrast_color(current_cell_color)
        current_cell_style = ('background-color:{}; color:{};'
                              .format(current_cell_color,
                                      current_cell_color_contrast)
                              )
        self.current_cell_color_button.setStyleSheet(current_cell_style)
