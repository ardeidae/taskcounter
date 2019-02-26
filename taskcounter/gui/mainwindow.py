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
import logging

from PyQt5.QtCore import (QByteArray, QItemSelectionModel, QMimeData, Qt,
                          pyqtSlot)
from PyQt5.QtGui import QBrush, QClipboard, QColor, QIcon, QPalette
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QFrame,
                             QGridLayout, QHBoxLayout, QHeaderView, QLabel,
                             QLCDNumber, QMainWindow, QSpinBox, QTableView,
                             QTimeEdit, QToolBar, QWidget, qApp)

from taskcounter import resources
from taskcounter.db import close_database
from taskcounter.enum import ResultColumn, TaskColumn, WeekDay
from taskcounter.gui import (AboutDialog, DurationEdit, FlowLayout,
                             SettingDialog, TaskNameDelegate)
from taskcounter.model import (SettingModel, SummaryModel, WeekModel,
                               get_total_annual_worked_hours)
from taskcounter.utility import (color_between, contrast_color,
                                 minutes_to_time_str, weekday_from_date,
                                 weeks_for_year)


class MainWindow(QMainWindow):
    """The main window of the application."""

    def __init__(self):
        """Construct a MainWindow."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.day_actions = dict()
        self.task_model = None
        self.task_view = None
        self.result_view = None
        self.result_model = SummaryModel(self)
        self.week_edit = None
        self.week_wrapper = None
        self.year_edit = None
        self.week_time_edit = None
        self.man_day_edit = None
        self.current_day_label = None
        self.week_time_lcd = None
        self.remaining_week_time_lcd = None
        self.day_time_lcd = None
        self.catch_up_lcd = None
        self.total_annual_lcd = None

    def closeEvent(self, event):
        """When application is about to close."""
        close_database()

    def __set_window_size(self):
        """Set the window size."""
        w = 700
        h = 400
        self.setMinimumWidth(w)
        self.setMinimumHeight(h)
        self.showMaximized()

    @staticmethod
    def __disable_headers_click(table):
        """Disable click on table headers."""
        table.horizontalHeader().setSectionsClickable(False)
        table.setCornerButtonEnabled(False)
        table.verticalHeader().setSectionsClickable(False)

    @staticmethod
    def __init_current_cell_color(table):
        """Initialize current cell color."""
        palette = table.palette()
        current_cell_color = SettingModel.current_cell_color()
        current_text_color = contrast_color(current_cell_color.name())
        palette.setBrush(QPalette.Highlight,
                         QBrush(QColor(current_cell_color)))
        palette.setBrush(QPalette.HighlightedText,
                         QBrush(QColor(current_text_color)))
        table.setPalette(palette)

    def __set_task_delegate(self, table):
        """Set a task delegate on a table."""
        delegate = TaskNameDelegate(table)
        table.setItemDelegateForColumn(
            TaskColumn.Task.value, delegate)

    def __resize_task_headers(self):
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

    def __resize_result_headers(self):
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

    def __init_layout(self):
        """Initialize the central widget layout."""
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QGridLayout()
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 20)
        main_layout.setRowStretch(3, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header_layout = FlowLayout()

        self.year_edit = QSpinBox(self)
        self.year_edit.setMinimum(2010)
        self.year_edit.setMaximum(2050)
        self.year_edit.setValue(datetime.datetime.now().year)

        year_widget = QWidget(self)
        year_layout = QHBoxLayout()
        year_widget.setLayout(year_layout)
        year_label = QLabel(self.tr('Year'), self)
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_edit)

        self.week_edit = QSpinBox(self)
        self.week_edit.setMinimum(1)
        self.__update_week_edit(self.year_edit.value())
        self.week_edit.setValue(datetime.date.today().isocalendar()[1])

        week_widget = QWidget(self)
        week_layout = QHBoxLayout()
        week_widget.setLayout(week_layout)
        week_label = QLabel(self.tr('Week'), self)
        week_layout.addWidget(week_label)
        week_layout.addWidget(self.week_edit)

        self.week_edit.valueChanged.connect(self.__week_changed)
        self.year_edit.valueChanged.connect(self.__year_changed)

        self.week_time_edit = DurationEdit(parent=self, hour_length=2)

        week_time_widget = QWidget(self)
        week_time_layout = QHBoxLayout()
        week_time_widget.setLayout(week_time_layout)
        week_time_label = QLabel(self.tr('Week time'), self)
        week_time_layout.addWidget(week_time_label)
        week_time_layout.addWidget(self.week_time_edit)

        self.week_time_edit.valueChanged.connect(self.__week_time_changed)

        self.man_day_edit = QTimeEdit(SettingModel.default_man_day_time(),
                                      self)

        man_day_widget = QWidget(self)
        man_day_layout = QHBoxLayout()
        man_day_widget.setLayout(man_day_layout)
        man_day_label = QLabel(self.tr('Man day time'), self)
        man_day_layout.addWidget(man_day_label)
        man_day_layout.addWidget(self.man_day_edit)

        self.man_day_edit.timeChanged.connect(self.__update_week_summary)

        header_layout.addWidget(year_widget)
        header_layout.addWidget(week_widget)
        header_layout.addWidget(week_time_widget)
        header_layout.addWidget(man_day_widget)

        main_layout.addLayout(header_layout, 0, 0, 1, 2)

        self.current_day_label = self.__build_title_label('')
        summary_label = self.__build_title_label(self.tr('Week summary'))

        main_layout.addWidget(self.current_day_label, 1, 0)
        main_layout.addWidget(summary_label, 1, 1)

        main_layout.addWidget(self.task_view, 2, 0)
        main_layout.addWidget(self.result_view, 2, 1)

        week_time_label = QLabel(self.tr('Week time'), self)
        self.week_time_lcd = self.__build_lcd_number_widget()

        remaining_week_label = QLabel(self.tr('Remaining week time'), self)
        self.remaining_week_time_lcd = self.__build_lcd_number_widget()

        day_label = QLabel(self.tr('Day time'), self)
        self.day_time_lcd = self.__build_lcd_number_widget()
        self.__change_day_color(QColor('#0000ff'))

        catch_up_label = QLabel(self.tr('Catch-up time'), self)
        self.catch_up_lcd = self.__build_lcd_number_widget()

        total_annual_label = QLabel(self.tr('Total annual time'), self)
        self.total_annual_lcd = self.__build_lcd_number_widget()

        footer_layout = QGridLayout()
        footer_layout.addWidget(day_label, 0, 0,
                                Qt.AlignHCenter)
        footer_layout.addWidget(week_time_label, 0, 1,
                                Qt.AlignHCenter)
        footer_layout.addWidget(remaining_week_label, 0, 2,
                                Qt.AlignCenter)
        footer_layout.addWidget(catch_up_label, 0, 3,
                                Qt.AlignCenter)
        footer_layout.addWidget(total_annual_label, 0, 4,
                                Qt.AlignCenter)
        footer_layout.addWidget(self.day_time_lcd, 1, 0)
        footer_layout.addWidget(self.week_time_lcd, 1, 1)
        footer_layout.addWidget(self.remaining_week_time_lcd, 1, 2)
        footer_layout.addWidget(self.catch_up_lcd, 1, 3)
        footer_layout.addWidget(self.total_annual_lcd, 1, 4)

        main_layout.addLayout(footer_layout, 3, 0, 1, 2)

        main_widget.setLayout(main_layout)

    def __set_day_title(self, title):
        """Set the day title on top of the table view."""
        self.logger.info('Set day title: %s', title)
        self.current_day_label.setText(str(title))

    def __change_week_color(self, color):
        """Change the lcd week color."""
        self.__change_lcd_number_color(self.week_time_lcd, color)
        self.__change_lcd_number_color(self.remaining_week_time_lcd, color)

    def __change_day_color(self, color):
        """Change the lcd day color."""
        self.__change_lcd_number_color(self.day_time_lcd, color)

    def __change_catch_up_color(self, color):
        """Change the lcd catch-up color."""
        self.__change_lcd_number_color(self.catch_up_lcd, color)

    @staticmethod
    def __change_lcd_number_color(lcd_widget, color):
        """Change a given lcd number color with a given color."""
        if isinstance(color, QColor) and isinstance(lcd_widget,
                                                    QLCDNumber):
            palette = QPalette()
            palette.setColor(QPalette.WindowText, color)
            lcd_widget.setPalette(palette)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.tr('Task counter'))
        self.setWindowIcon(QIcon(':/tasks.png'))
        self.statusBar()

        self.__set_window_size()
        self.__create_toolbars_and_menus()

        self.task_view = QTableView(self)
        self.__init_current_cell_color(self.task_view)
        self.__disable_headers_click(self.task_view)
        self.task_view.setSelectionMode(QTableView.SingleSelection)
        self.__set_task_delegate(self.task_view)

        self.result_view = QTableView(self)
        self.__init_current_cell_color(self.result_view)
        self.__disable_headers_click(self.result_view)
        self.result_view.setAlternatingRowColors(True)
        self.result_view.setModel(self.result_model)
        self.result_view.setSelectionBehavior(QTableView.SelectRows)
        self.__init_layout()

        self.__validate_week_and_year()

        self.show()

    def __create_toolbars_and_menus(self):
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

            if day == WeekDay.Monday:
                tr_name = self.tr('Monday')
            elif day == WeekDay.Tuesday:
                tr_name = self.tr('Tuesday')
            elif day == WeekDay.Wednesday:
                tr_name = self.tr('Wednesday')
            elif day == WeekDay.Thursday:
                tr_name = self.tr('Thursday')
            elif day == WeekDay.Friday:
                tr_name = self.tr('Friday')
            elif day == WeekDay.Saturday:
                tr_name = self.tr('Saturday')
            elif day == WeekDay.Sunday:
                tr_name = self.tr('Sunday')

            action = QAction(
                QIcon(':/' + day.name.lower() + '.png'), tr_name, self)
            action.setObjectName(day.name)
            action.setShortcut('Alt+' + str(counter))
            action.setCheckable(True)
            action.setStatusTip(self.tr('Go to {day}').format(day=tr_name))
            action.triggered.connect(self.__change_current_day)
            days_action_group.addAction(action)
            self.day_actions[day] = action
            toolbar_days.addAction(action)

        previous_act = QAction(QIcon(':/previous.png'),
                               self.tr('Previous Week'), self)
        previous_act.setShortcut('Ctrl+P')
        previous_act.triggered.connect(self.__previous_week)
        previous_act.setStatusTip(self.tr('Go to Previous Week'))

        next_act = QAction(QIcon(':/next.png'), self.tr('Next Week'), self)
        next_act.setShortcut('Ctrl+N')
        next_act.triggered.connect(self.__next_week)
        next_act.setStatusTip(self.tr('Go to Next Week'))

        today_act = QAction(QIcon(':/today.png'), self.tr('Today'), self)
        today_act.setShortcut('Ctrl+T')
        today_act.triggered.connect(self.__today)
        today_act.setStatusTip(self.tr('Go to today'))

        about_act = QAction(QIcon(':/info.png'), self.tr('About'), self)
        about_act.triggered.connect(self.__about)
        about_act.setStatusTip(self.tr('About this application'))

        about_qt_act = QAction(self.tr('About Qt'), self)
        about_qt_act.triggered.connect(qApp.aboutQt)
        about_qt_act.setStatusTip(self.tr('About Qt'))

        settings_act = QAction(QIcon(':/settings.png'),
                               self.tr('Preferences'), self)
        settings_act.triggered.connect(self.__edit_preferences)
        settings_act.setStatusTip(self.tr('Edit preferences'))

        exit_act = QAction(QIcon(':/exit.png'), self.tr('&Quit'), self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip(self.tr('Quit application'))
        exit_act.triggered.connect(self.close)

        export_act = QAction(QIcon(':/export.png'), self.tr('Export'), self)
        export_act.setShortcut('Ctrl+E')
        export_act.setStatusTip(self.tr('Export week summary as html table'))
        export_act.triggered.connect(self.__export)

        toolbar_weeks.addAction(today_act)
        toolbar_weeks.addAction(previous_act)
        toolbar_weeks.addAction(next_act)
        toolbar_weeks.addAction(export_act)

        toolbar_application.addAction(exit_act)
        toolbar_application.addAction(settings_act)
        toolbar_application.addAction(about_act)

        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(True)

        app_menu = menu_bar.addMenu(self.tr('Application'))
        app_menu.addAction(about_act)
        app_menu.addAction(about_qt_act)
        app_menu.addAction(settings_act)
        app_menu.addAction(exit_act)

        weeks_menu = menu_bar.addMenu(self.tr('Weeks'))
        weeks_menu.addAction(today_act)
        weeks_menu.addAction(previous_act)
        weeks_menu.addAction(next_act)
        weeks_menu.addAction(export_act)

        days_menu = menu_bar.addMenu(self.tr('Days'))
        for action in days_action_group.actions():
            days_menu.addAction(action)

    def __validate_week_and_year(self):
        """Validate the week and the year and update a WeekModel."""
        self.week_wrapper = WeekModel(
            self.year_edit.value(), self.week_edit.value(), self)
        self.logger.debug('Week wrapper: %s', self.week_wrapper)

        self.week_time_edit.blockSignals(True)
        self.week_time_edit.minutes = self.week_wrapper.minutes_to_work
        self.week_time_edit.blockSignals(False)

        if (self.year_edit.value() == datetime.datetime.now().year
                and self.week_edit.value() ==
                datetime.date.today().isocalendar()[1]):
            self.day_actions[weekday_from_date(
                datetime.date.today())].activate(QAction.Trigger)
        else:
            self.day_actions[WeekDay.Monday].activate(QAction.Trigger)

    @pyqtSlot()
    def __previous_week(self):
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
    def __next_week(self):
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
    def __today(self):
        """Go to the current day, today."""
        self.year_edit.setValue(datetime.datetime.now().year)
        self.__update_week_edit(self.year_edit.value())
        self.week_edit.setValue(datetime.date.today().isocalendar()[1])
        self.__validate_week_and_year()

    @pyqtSlot()
    def __about(self):
        """Open the about page."""
        about = AboutDialog(self)
        about.exec_()

    @pyqtSlot()
    def __export(self):
        """Export data."""
        self.__export_cells_as_table()

    @pyqtSlot()
    def __edit_preferences(self):
        """Edit preferences."""
        settings = SettingDialog(self)
        settings.exec_()

        self.__update_settings()

    @pyqtSlot()
    def __change_current_day(self):
        """Change the current day for edition."""
        sender = self.sender()
        if self.week_wrapper:
            if self.task_model:
                self.task_model.dataChanged.disconnect()
            self.task_model = self.week_wrapper[WeekDay[sender.objectName()]]
            self.__update_time()
            self.task_model.dataChanged.connect(
                self.__update_time)

            # set readable date in title
            self.__set_day_title(
                self.task_model.date.strftime('%A %d %B %Y'))
            self.task_view.setModel(self.task_model)

            self.__resize_task_headers()

            # the table takes the focus
            self.task_view.setFocus(Qt.OtherFocusReason)

            # the last task cell is selected
            flags = QItemSelectionModel.ClearAndSelect
            index = self.task_model.last_task_cell_index
            self.task_view.selectionModel().setCurrentIndex(index, flags)

    @pyqtSlot(int)
    def __year_changed(self, year):
        """Change the current year, event."""
        self.__update_week_edit(year)
        self.__validate_week_and_year()

    @pyqtSlot()
    def __week_changed(self):
        """Change the current week, event."""
        self.__validate_week_and_year()

    def __update_week_edit(self, year):
        """Update the week edit max value for a given year."""
        weeks = weeks_for_year(int(year))
        self.week_edit.setMaximum(weeks)

    @pyqtSlot()
    def __update_time(self):
        """Update time counters."""
        self.__update_day_time_counter()
        self.__update_week_time_counter()
        self.__update_catch_up_time_counter()
        self.__update_total_annual_time_counter()
        self.__update_week_summary()

    def __update_day_time_counter(self):
        """Update the day time counter."""
        self.day_time_lcd.display(
            minutes_to_time_str(self.task_model.minutes_of_day))

    def __update_week_time_counter(self):
        """Update the week time counters."""
        self.week_time_lcd.display(
            minutes_to_time_str(self.week_wrapper.minutes_of_week))
        self.remaining_week_time_lcd.display(
            minutes_to_time_str(max(0, self.week_wrapper.minutes_to_work
                                    - self.week_wrapper.minutes_of_week)))

        self.__update_week_counter_color()

    def __update_catch_up_time_counter(self):
        """Update the catch-up time counter."""
        to_work = self.week_wrapper.total_time_to_work
        worked = self.week_wrapper.total_time_worked

        catch_up_time = worked - to_work
        abs_time = abs(catch_up_time)
        time_str = minutes_to_time_str(abs_time)

        if catch_up_time >= 0:
            self.__change_catch_up_color(SettingModel.valid_color())
            self.catch_up_lcd.setToolTip('+' + time_str)
        else:
            self.__change_catch_up_color(SettingModel.invalid_color())
            self.catch_up_lcd.setToolTip('-' + time_str)

        if abs_time >= 6000:
            self.catch_up_lcd.display(abs_time // 60)
        else:
            self.catch_up_lcd.display(time_str)

    def __update_total_annual_time_counter(self):
        """Update the total annual time counter."""
        total = get_total_annual_worked_hours(self.year_edit.value())
        self.total_annual_lcd.display(total)

    def __build_lcd_number_widget(self):
        """Build a LCD Number widget."""
        lcdnumber = QLCDNumber(self)
        lcdnumber.setSegmentStyle(QLCDNumber.Filled)
        lcdnumber.setFixedHeight(40)
        lcdnumber.setFrameStyle(QFrame.NoFrame)
        return lcdnumber

    @pyqtSlot()
    def __week_time_changed(self):
        """Change the work time of the week, event."""
        self.__update_week_time()

    def __update_week_time(self):
        """Update the work time of the week."""
        minutes_time = self.week_time_edit.minutes
        if self.week_wrapper:
            self.week_wrapper.minutes_to_work = minutes_time
        self.__update_week_counter_color()
        self.__update_catch_up_time_counter()
        self.__update_week_time_counter()

    def __update_week_counter_color(self):
        """Update the week counter color depending on the time percentage."""
        percent = 1
        if self.week_wrapper.minutes_to_work:
            # denominator cannot be zero
            percent = (self.week_wrapper.minutes_of_week /
                       self.week_wrapper.minutes_to_work)

        color = color_between(SettingModel.invalid_color().name(),
                              SettingModel.valid_color().name(), percent)
        self.__change_week_color(QColor(color))

    def __build_title_label(self, title):
        """Build a label widget with a given title."""
        label = QLabel(title, self)
        label.setAlignment(Qt.AlignCenter)
        label.setMargin(5)
        font = label.font()
        font.setBold(True)
        font.setPointSize(16)
        label.setFont(font)
        return label

    def __update_week_summary(self):
        """Update the week summary."""
        if self.week_wrapper:

            man_day_time = self.man_day_edit.time()
            man_day_minutes = man_day_time.hour() * 60 + man_day_time.minute()

            tasks = self.week_wrapper.week_summary(man_day_minutes)
            self.result_model.tasks = tasks
            self.__resize_result_headers()

    def __export_cells_as_table(self):
        """Copy tasks and time cells as html table."""
        model = self.result_view.model()

        table_text = '<html><head>'
        table_text += '<meta http-equiv="content-type" '
        table_text += 'content="text/html; charset=utf-8">'
        table_text += '</head><body>'
        table_text += '<table cellpadding="0" cellspacing="0" border="0" '
        table_text += 'style="width:100%;">'

        table_text += '<tr>'
        table_text += ('<th style="border:2px solid black;'
                       'margin:0;padding:2px;text-align:center;'
                       'background-color:#ddd;">'
                       + self.tr('Task') + '</th>')
        table_text += ('<th style="border:2px solid black;'
                       'margin:0;padding:2px;text-align:center;'
                       'background-color:#ddd;width:20%;">'
                       + self.tr('Time') + '</th>')
        table_text += '</tr>'

        rows = model.rowCount()
        columns_to_export = (ResultColumn.Task.value, ResultColumn.Time.value)

        for i in range(0, rows):
            table_text += '<tr>'
            for j in columns_to_export:
                content = model.data(model.index(i, j), Qt.DisplayRole)
                if j == 0:
                    table_text += ('<td style="border:2px solid black;'
                                   'margin:0;padding:2px;text-align:left;">'
                                   '{}</td>'
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

    def __update_settings(self):
        """Update user interface with new settings."""
        self.__init_current_cell_color(self.task_view)
        self.__init_current_cell_color(self.result_view)
        self.__update_time()
        self.man_day_edit.setTime(SettingModel.default_man_day_time())
