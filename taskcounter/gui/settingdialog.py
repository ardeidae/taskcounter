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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QColorDialog, QDialog, QGridLayout, QLabel,
                             QPushButton, QTimeEdit)

from taskcounter.gui import CenterMixin
from taskcounter.model import SettingModel
from taskcounter.utility import contrast_color


class SettingDialog(CenterMixin, QDialog):
    """Settings dialog."""

    def __init__(self, parent=None):
        """Construct a settings dialog."""
        super().__init__(parent)
        self.setWindowTitle('Edit preferences')
        self.center()

        self.invalid_color = None
        self.valid_color = None
        self.current_cell_color = None

        self.__update_colors__()

        manday_time_label = QLabel('Default man day time', self)
        self.manday_time = QTimeEdit(
            SettingModel.default_manday_time(), self)
        self.manday_time.timeChanged.connect(
            self.__manday_time_changed__)

        invalid_color_label = QLabel('Invalid color', self)
        self.invalid_color_button = QPushButton('Text', self)
        self.invalid_color_button.clicked.connect(
            self.__open_invalid_color_dialog__)

        valid_color_label = QLabel('Valid color', self)
        self.valid_color_button = QPushButton('Text', self)
        self.valid_color_button.clicked.connect(
            self.__open_valid_color_dialog__)

        current_cell_color_label = QLabel('Current cell color', self)
        self.current_cell_color_button = QPushButton('Text', self)
        self.current_cell_color_button.clicked.connect(
            self.__open_current_cell_color_dialog__)

        self.__update_buttons_colors__()

        main_layout = QGridLayout()

        main_layout.addWidget(manday_time_label, 0, 0)
        main_layout.addWidget(self.manday_time, 0, 1)

        main_layout.addWidget(invalid_color_label, 1, 0)
        main_layout.addWidget(self.invalid_color_button, 1, 1)

        main_layout.addWidget(valid_color_label, 2, 0)
        main_layout.addWidget(self.valid_color_button, 2, 1)

        main_layout.addWidget(current_cell_color_label, 3, 0)
        main_layout.addWidget(self.current_cell_color_button, 3, 1)

        self.setLayout(main_layout)

    @pyqtSlot()
    def __manday_time_changed__(self):
        """Update the man day time setting."""
        SettingModel.set_default_manday_time(self.manday_time.time())

    @pyqtSlot()
    def __open_invalid_color_dialog__(self):
        """Update the invalid color setting."""
        color = QColorDialog.getColor(self.invalid_color, self,
                                      'Select invalid color',
                                      QColorDialog.DontUseNativeDialog)
        if color.isValid():
            SettingModel.set_invalid_color(color)

        self.__update_colors__()
        self.__update_buttons_colors__()

    @pyqtSlot()
    def __open_valid_color_dialog__(self):
        """Update the valid color setting."""
        color = QColorDialog.getColor(self.valid_color, self,
                                      'Select invalid color',
                                      QColorDialog.DontUseNativeDialog)
        if color.isValid():
            SettingModel.set_valid_color(color)

        self.__update_colors__()
        self.__update_buttons_colors__()

    @pyqtSlot()
    def __open_current_cell_color_dialog__(self):
        """Update the current cell color setting."""
        color = QColorDialog.getColor(self.current_cell_color, self,
                                      'Select current cell color',
                                      QColorDialog.DontUseNativeDialog)
        if color.isValid():
            SettingModel.set_current_cell_color(color)

        self.__update_colors__()
        self.__update_buttons_colors__()

    def __update_colors__(self):
        """Update the local colors values."""
        self.invalid_color = SettingModel.invalid_color()
        self.valid_color = SettingModel.valid_color()
        self.current_cell_color = SettingModel.current_cell_color()

    def __update_buttons_colors__(self):
        """Update the buttons colors."""
        invalid_color = self.invalid_color.name()
        invalid_color_constrast = contrast_color(invalid_color)
        invalid_style = ('background-color:{}; color:{};'
                         .format(invalid_color, invalid_color_constrast)
                         )
        self.invalid_color_button.setStyleSheet(invalid_style)

        valid_color = self.valid_color.name()
        valid_color_constrast = contrast_color(valid_color)
        valid_style = ('background-color:{}; color:{};'
                       .format(valid_color, valid_color_constrast)
                       )
        self.valid_color_button.setStyleSheet(valid_style)

        current_cell_color = self.current_cell_color.name()
        current_cell_color_constrast = contrast_color(current_cell_color)
        current_cell_style = ('background-color:{}; color:{};'
                              .format(current_cell_color,
                                      current_cell_color_constrast)
                              )
        self.current_cell_color_button.setStyleSheet(current_cell_style)
