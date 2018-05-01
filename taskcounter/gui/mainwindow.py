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

"""Task counter main window."""

import datetime

from PyQt5.QtCore import (QByteArray, QItemSelectionModel, QMimeData, Qt,
                          pyqtSlot)
from PyQt5.QtGui import QBrush, QClipboard, QColor, QIcon, QPalette
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QFrame,
                             QGridLayout, QHeaderView, QLabel, QLCDNumber,
                             QMainWindow, QSpinBox, QTableView, QTimeEdit,
                             QToolBar, QWidget, qApp)

from taskcounter import resources
from taskcounter.db import close_database
from taskcounter.enum import ResultColumn, TaskColumn, WeekDay
from taskcounter.model import (SummaryModel, SettingModel, WeekModel)
from taskcounter.utility import (color_between, contrast_color,
                                 minutes_to_time_str, weekday_from_date,
                                 weeks_for_year)

from taskcounter.gui import AboutDialog, SettingDialog, TaskNameDelegate


class MainWindow(QMainWindow):
    """The main window of the application."""

    def __init__(self):
        """Construct a MainWindow."""
        super().__init__()
        self.day_actions = dict()
        self.task_model = None
        self.task_view = None
        self.result_view = None
        self.result_model = SummaryModel(self)
        self.week_edit = None
        self.week_wrapper = None
        self.year_edit = None
        self.hours_edit = None
        self.minutes_edit = None
        self.manday_tedit = None
        self.current_day_label = None
        self.week_time_lcdnumber = None
        self.day_time_lcdnumber = None
        self.catch_up_lcdnumber = None

    def closeEvent(self, event):
        """When application is about to close."""
        close_database()

    def __set_window_size__(self):
        """Set the window size."""
        w = 700
        h = 400
        self.setMinimumWidth(w)
        self.setMinimumHeight(h)
        self.showMaximized()

    def __disable_headers_click__(self, table):
        """Disable click on table headers."""
        table.horizontalHeader().setSectionsClickable(False)
        table.setCornerButtonEnabled(False)
        table.verticalHeader().setSectionsClickable(False)

    def __init_current_cell_color__(self, table):
        """Initialize current cell color."""
        palette = table.palette()
        current_cell_color = SettingModel.current_cell_color()
        current_text_color = contrast_color(current_cell_color.name())
        palette.setBrush(QPalette.Highlight,
                         QBrush(QColor(current_cell_color)))
        palette.setBrush(QPalette.HighlightedText,
                         QBrush(QColor(current_text_color)))
        table.setPalette(palette)

    def __set_task_delegate__(self, table):
        """Set a task delegate on a table."""
        delegate = TaskNameDelegate(table)
        table.setItemDelegateForColumn(
            TaskColumn.Task.value, delegate)

    def __resize_task_headers__(self):
        """Resize task headers."""
        self.task_view.hideColumn(TaskColumn.Id.value)
        self.task_view.horizontalHeader().setSectionResizeMode(
            TaskColumn.Task.value,
            QHeaderView.Stretch)
        self.task_view.horizontalHeader().setSectionResizeMode(
            TaskColumn.Start_Time.value,
            QHeaderView.Fixed)
        self.task_view.horizontalHeader().resizeSection(
            TaskColumn.Start_Time.value, 70)

        self.task_view.horizontalHeader().setSectionResizeMode(
            TaskColumn.End_Time.value, QHeaderView.Fixed)
        self.task_view.horizontalHeader().resizeSection(
            TaskColumn.End_Time.value,
            70)

    def __resize_result_headers__(self):
        """Resize result headers."""
        self.result_view.horizontalHeader().setSectionResizeMode(
            ResultColumn.Task.value,
            QHeaderView.Stretch)
        self.result_view.horizontalHeader().setSectionResizeMode(
            ResultColumn.Time.value,
            QHeaderView.Fixed)
        self.result_view.horizontalHeader().setSectionResizeMode(
            ResultColumn.Man_Day.value,
            QHeaderView.Fixed)
        self.result_view.horizontalHeader().resizeSection(
            ResultColumn.Time.value, 70)
        self.result_view.horizontalHeader().resizeSection(
            ResultColumn.Man_Day.value, 70)

    def __init_layout__(self):
        """Initialize the central widget layout."""
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QGridLayout()
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 20)
        main_layout.setRowStretch(2, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.current_day_label = self.__build_title_label__('')
        summary_label = self.__build_title_label__('Week summary')

        main_layout.addWidget(self.current_day_label, 0, 0)
        main_layout.addWidget(summary_label, 0, 1)

        main_layout.addWidget(self.task_view, 1, 0)
        main_layout.addWidget(self.result_view, 1, 1)

        week_label = QLabel('Week time', self)
        self.week_time_lcdnumber = self.__build_lcd_number_widget__()

        day_label = QLabel('Day time', self)
        self.day_time_lcdnumber = self.__build_lcd_number_widget__()
        self.__change_day_color__(QColor('#0000ff'))

        catch_up_label = QLabel('Catch-up time', self)
        self.catch_up_lcdnumber = self.__build_lcd_number_widget__()

        footer_layout = QGridLayout()
        footer_layout.addWidget(day_label, 0, 0,
                                Qt.AlignHCenter)
        footer_layout.addWidget(week_label, 0, 1,
                                Qt.AlignHCenter)
        footer_layout.addWidget(catch_up_label, 0, 2,
                                Qt.AlignHCenter)
        footer_layout.addWidget(self.day_time_lcdnumber, 1, 0)
        footer_layout.addWidget(self.week_time_lcdnumber, 1, 1)
        footer_layout.addWidget(self.catch_up_lcdnumber, 1, 2)

        main_layout.addLayout(footer_layout, 2, 0, 1, 2)

        main_widget.setLayout(main_layout)

    def __set_day_title__(self, title):
        """Set the day title on top of the table view."""
        self.current_day_label.setText(str(title))

    def __change_week_color__(self, color):
        """Change the lcd week color."""
        self.__change_lcd_number_color__(self.week_time_lcdnumber, color)

    def __change_day_color__(self, color):
        """Change the lcd day color."""
        self.__change_lcd_number_color__(self.day_time_lcdnumber, color)

    def __change_catch_up_color__(self, color):
        """Change the lcd catch-up color."""
        self.__change_lcd_number_color__(self.catch_up_lcdnumber, color)

    def __change_lcd_number_color__(self, lcd_widget, color):
        """Change a given lcd number color with a given color."""
        if isinstance(color, QColor) and isinstance(lcd_widget,
                                                    QLCDNumber):
            palette = QPalette()
            palette.setColor(QPalette.WindowText, color)
            lcd_widget.setPalette(palette)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Task counter')
        self.setWindowIcon(QIcon(':/tasks.png'))
        self.statusBar()

        self.__set_window_size__()
        self.__create_toolbars_and_menus__()

        self.task_view = QTableView(self)
        self.__init_current_cell_color__(self.task_view)
        self.__disable_headers_click__(self.task_view)
        self.task_view.setSelectionMode(QTableView.SingleSelection)
        self.__set_task_delegate__(self.task_view)

        self.result_view = QTableView(self)
        self.__init_current_cell_color__(self.result_view)
        self.__disable_headers_click__(self.result_view)
        self.result_view.setAlternatingRowColors(True)
        self.result_view.setModel(self.result_model)
        self.result_view.setSelectionBehavior(QTableView.SelectRows)
        self.__init_layout__()

        self.__validate_week_and_year__()

        self.show()

    def __create_toolbars_and_menus__(self):
        """Create the toolbars and menus."""
        toolbar_weeks = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, toolbar_weeks)
        toolbar_application = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, toolbar_application)
        self.addToolBarBreak()
        toolbar_days = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, toolbar_days)

        days_action_group = QActionGroup(self)
        for counter, day in enumerate(WeekDay, start=1):
            action = QAction(
                QIcon(':/' + day.name.lower() + '.png'), day.name, self)
            action.setShortcut('Alt+' + str(counter))
            action.setCheckable(True)
            action.setStatusTip('Go to ' + day.name)
            action.triggered.connect(self.__change_current_day__)
            days_action_group.addAction(action)
            self.day_actions[day] = action
            toolbar_days.addAction(action)

        previous_act = QAction(QIcon(':/previous.png'), 'Previous Week', self)
        previous_act.setShortcut('Ctrl+P')
        previous_act.triggered.connect(self.__previous_week__)
        previous_act.setStatusTip('Go to Previous Week')

        next_act = QAction(QIcon(':/next.png'), 'Next Week', self)
        next_act.setShortcut('Ctrl+N')
        next_act.triggered.connect(self.__next_week__)
        next_act.setStatusTip('Go to Next Week')

        today_act = QAction(QIcon(':/today.png'), 'Today', self)
        today_act.setShortcut('Ctrl+T')
        today_act.triggered.connect(self.__today__)
        today_act.setStatusTip('Go to today')

        about_act = QAction(QIcon(':/info.png'), 'About', self)
        about_act.triggered.connect(self.__about__)
        about_act.setStatusTip('About this application')

        about_qt_act = QAction('About Qt', self)
        about_qt_act.triggered.connect(qApp.aboutQt)
        about_qt_act.setStatusTip('About Qt')

        settings_act = QAction(QIcon(':/settings.png'), 'Preferences', self)
        settings_act.triggered.connect(self.__edit_preferences__)
        settings_act.setStatusTip('Edit preferences')

        exit_act = QAction(QIcon(':/exit.png'), '&Quit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Quit application')
        exit_act.triggered.connect(self.close)

        export_act = QAction(QIcon(':/export.png'), 'Export', self)
        export_act.setShortcut('Ctrl+E')
        export_act.setStatusTip('Export week summary as html table')
        export_act.triggered.connect(self.__export__)

        self.year_edit = QSpinBox(self)
        self.year_edit.setPrefix('Year: ')
        self.year_edit.setMinimum(2010)
        self.year_edit.setMaximum(2050)
        self.year_edit.setValue(datetime.datetime.now().year)

        self.week_edit = QSpinBox(self)
        self.week_edit.setPrefix('Week: ')
        self.week_edit.setMinimum(1)
        self.__update_week_edit__(self.year_edit.value())
        self.week_edit.setValue(datetime.date.today().isocalendar()[1])

        self.week_edit.valueChanged.connect(self.__week_changed__)
        self.year_edit.valueChanged.connect(self.__year_changed__)

        self.hours_edit = QSpinBox(self)
        self.hours_edit.setSuffix('h')
        self.hours_edit.setMinimum(0)
        self.hours_edit.setMaximum(84)

        self.minutes_edit = QSpinBox(self)
        self.minutes_edit.setSuffix('m')
        self.minutes_edit.setMinimum(0)
        self.minutes_edit.setMaximum(59)

        self.hours_edit.valueChanged.connect(self.__hours_changed__)
        self.minutes_edit.valueChanged.connect(self.__minutes_changed__)

        self.manday_tedit = QTimeEdit(SettingModel.default_manday_time(),
                                      self)
        self.manday_tedit.timeChanged.connect(self.__update_week_summary__)

        toolbar_weeks.addAction(today_act)
        toolbar_weeks.addWidget(self.year_edit)
        toolbar_weeks.addWidget(self.week_edit)
        toolbar_weeks.addAction(previous_act)
        toolbar_weeks.addAction(next_act)
        toolbar_weeks.addWidget(self.hours_edit)
        toolbar_weeks.addWidget(self.minutes_edit)
        toolbar_weeks.addAction(export_act)
        toolbar_weeks.addWidget(self.manday_tedit)

        toolbar_application.addAction(exit_act)
        toolbar_application.addAction(settings_act)
        toolbar_application.addAction(about_act)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(True)

        app_menu = menubar.addMenu('Application')
        app_menu.addAction(about_act)
        app_menu.addAction(about_qt_act)
        app_menu.addAction(settings_act)
        app_menu.addAction(exit_act)

        weeks_menu = menubar.addMenu('Weeks')
        weeks_menu.addAction(today_act)
        weeks_menu.addAction(previous_act)
        weeks_menu.addAction(next_act)
        weeks_menu.addAction(export_act)

        days_menu = menubar.addMenu('Days')
        for action in days_action_group.actions():
            days_menu.addAction(action)

    def __validate_week_and_year__(self):
        """Validate the week and the year and update a WeekModel."""
        self.week_wrapper = WeekModel(
            self.year_edit.value(), self.week_edit.value(), self)

        minutes_time = self.week_wrapper.minutes_to_work
        (hours, minutes) = divmod(minutes_time, 60)

        self.hours_edit.blockSignals(True)
        self.minutes_edit.blockSignals(True)
        self.hours_edit.setValue(hours)
        self.minutes_edit.setValue(minutes)
        self.hours_edit.blockSignals(False)
        self.minutes_edit.blockSignals(False)

        if (self.year_edit.value() == datetime.datetime.now().year
                and self.week_edit.value() ==
                datetime.date.today().isocalendar()[1]):
            self.day_actions[weekday_from_date(
                datetime.date.today())].activate(QAction.Trigger)
        else:
            self.day_actions[WeekDay.Monday].activate(QAction.Trigger)

    @pyqtSlot()
    def __previous_week__(self):
        """Go to the previous week."""
        current_week = int(self.week_edit.value())
        if current_week - 1 == 0:
            current_year = int(self.year_edit.value())
            weeks_of_previous_year = weeks_for_year(current_year - 1)
            self.week_edit.setValue(weeks_of_previous_year)
            self.year_edit.setValue(current_year - 1)
        else:
            self.week_edit.setValue(current_week - 1)

    @pyqtSlot()
    def __next_week__(self):
        """Go to the next week."""
        current_week = int(self.week_edit.value())
        current_year = int(self.year_edit.value())
        weeks_of_current_year = weeks_for_year(current_year)
        if current_week + 1 > weeks_of_current_year:
            self.week_edit.setValue(1)
            self.year_edit.setValue(current_year + 1)
        else:
            self.week_edit.setValue(current_week + 1)

    @pyqtSlot()
    def __today__(self):
        """Go to the current day, today."""
        self.year_edit.setValue(datetime.datetime.now().year)
        self.__update_week_edit__(self.year_edit.value())
        self.week_edit.setValue(datetime.date.today().isocalendar()[1])
        self.__validate_week_and_year__()

    @pyqtSlot()
    def __about__(self):
        """Open the about page."""
        about = AboutDialog(self)
        about.exec_()

    @pyqtSlot()
    def __export__(self):
        """Export data."""
        self.__export_cells_as_table__()

    @pyqtSlot()
    def __edit_preferences__(self):
        """Edit preferences."""
        settings = SettingDialog(self)
        settings.exec_()

        self.__update_settings__()

    @pyqtSlot()
    def __change_current_day__(self):
        """Change the current day for edition."""
        sender = self.sender()
        if self.week_wrapper:
            if self.task_model:
                self.task_model.dataChanged.disconnect()
            self.task_model = self.week_wrapper[WeekDay[sender.text()]]
            self.__update_time__()
            self.task_model.dataChanged.connect(
                self.__update_time__)

            # set readable date in title
            self.__set_day_title__(
                self.task_model.date.strftime('%A %d %B %Y'))
            self.task_view.setModel(self.task_model)

            self.__resize_task_headers__()

            # the table takes the focus
            self.task_view.setFocus(Qt.OtherFocusReason)

            # the last task cell is selected
            flags = QItemSelectionModel.ClearAndSelect
            index = self.task_model.last_task_cell_index
            self.task_view.selectionModel().setCurrentIndex(index, flags)

    @pyqtSlot(int)
    def __year_changed__(self, year):
        """Change the current year, event."""
        self.__update_week_edit__(year)
        self.__validate_week_and_year__()

    @pyqtSlot()
    def __week_changed__(self):
        """Change the current week, event."""
        self.__validate_week_and_year__()

    def __update_week_edit__(self, year):
        """Update the week edit max value for a given year."""
        weeks = weeks_for_year(int(year))
        self.week_edit.setMaximum(weeks)

    @pyqtSlot()
    def __update_time__(self):
        """Update time counters."""
        self.__update_day_time_counter__()
        self.__update_week_time_counter__()
        self.__update_catch_up_time_counter__()
        self.__update_week_summary__()

    def __update_day_time_counter__(self):
        """Update the day time counter."""
        self.day_time_lcdnumber.display(
            minutes_to_time_str(self.task_model.minutes_of_day))

    def __update_week_time_counter__(self):
        """Update the week time counter."""
        self.week_time_lcdnumber.display(
            minutes_to_time_str(self.week_wrapper.minutes_of_week))

        self.__update_week_counter_color__()

    def __update_catch_up_time_counter__(self):
        """Update the catch-up time counter."""
        to_work = self.week_wrapper.total_time_to_work
        worked = self.week_wrapper.total_time_worked

        catch_up_time = worked - to_work
        abs_time = abs(catch_up_time)
        time_str = minutes_to_time_str(abs_time)

        if catch_up_time >= 0:
            self.__change_catch_up_color__(SettingModel.valid_color())
            self.catch_up_lcdnumber.setToolTip('+' + time_str)
        else:
            self.__change_catch_up_color__(SettingModel.invalid_color())
            self.catch_up_lcdnumber.setToolTip('-' + time_str)

        if abs_time >= 6000:
            self.catch_up_lcdnumber.display(abs_time // 60)
        else:
            self.catch_up_lcdnumber.display(time_str)

    def __build_lcd_number_widget__(self):
        """Build a LCD Number widget."""
        lcdnumber = QLCDNumber(self)
        lcdnumber.setSegmentStyle(QLCDNumber.Filled)
        lcdnumber.setFixedHeight(40)
        lcdnumber.setFrameStyle(QFrame.NoFrame)
        return lcdnumber

    @pyqtSlot()
    def __hours_changed__(self):
        """Change the work hours of the week, event."""
        self.__update_week_time__()

    @pyqtSlot()
    def __minutes_changed__(self):
        """Change the work minutes of the week, event."""
        self.__update_week_time__()

    def __update_week_time__(self):
        """Update the work time of the week."""
        hours = self.hours_edit.value()
        minutes = self.minutes_edit.value()
        minutes_time = 60 * hours + minutes
        if self.week_wrapper:
            self.week_wrapper.minutes_to_work = minutes_time
        self.__update_week_counter_color__()
        self.__update_catch_up_time_counter__()

    def __update_week_counter_color__(self):
        """Update the week counter color depending on the time percentage."""
        percent = 1
        if self.week_wrapper.minutes_to_work:
            # denominator cannot be zero
            percent = (self.week_wrapper.minutes_of_week /
                       self.week_wrapper.minutes_to_work)

        color = color_between(SettingModel.invalid_color().name(),
                              SettingModel.valid_color().name(), percent)
        self.__change_week_color__(QColor(color))

    def __build_title_label__(self, title):
        """Build a label widget with a given title."""
        label = QLabel(title, self)
        label.setAlignment(Qt.AlignCenter)
        label.setMargin(5)
        font = label.font()
        font.setBold(True)
        font.setPointSize(16)
        label.setFont(font)
        return label

    def __update_week_summary__(self):
        """Update the week summary."""
        if self.week_wrapper:

            manday_time = self.manday_tedit.time()
            manday_minutes = manday_time.hour() * 60 + manday_time.minute()

            tasks = self.week_wrapper.week_summary(manday_minutes)
            self.result_model.tasks = tasks
            self.__resize_result_headers__()

    def __export_cells_as_table__(self):
        """Copy tasks and time cells as html table."""
        model = self.result_view.model()

        table_text = '<html><head>'
        table_text += '<meta http-equiv="content-type" '
        table_text += 'content="text/html; charset=utf-8">'
        table_text += '</head><body>'
        table_text += '<table cellpadding="0" cellspacing="0" border="0" '
        table_text += 'style="width:100%;">'

        rows = model.rowCount()
        columns_to_export = (ResultColumn.Task.value, ResultColumn.Time.value)

        for i in range(0, rows):
            table_text += '<tr>'
            for j in columns_to_export:
                content = model.data(model.index(i, j), Qt.DisplayRole)
                if j == 0:
                    table_text += ('<th style="border:2px solid black;'
                                   'margin:0;padding:2px;text-align:left;'
                                   'background-color:#ddd;">{}</th>'
                                   ).format(content)
                else:
                    table_text += ('<td style="border:2px solid black;'
                                   'margin:0;padding:2px;text-align:center;'
                                   'width:20%;">{}</td>'
                                   ).format(content)
            table_text += '</tr>'

        table_text += '</tr></table></body></html>'

        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        bytes_array = QByteArray()
        bytes_array.append(table_text)
        mime_data.setData('text/html', bytes_array)

        clipboard.setMimeData(mime_data, QClipboard.Clipboard)

    def __update_settings__(self):
        """Update user interface with new settings."""
        self.__init_current_cell_color__(self.task_view)
        self.__init_current_cell_color__(self.result_view)
        self.__update_time__()
        self.manday_tedit.setTime(SettingModel.default_manday_time())
