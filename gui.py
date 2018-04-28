#     Copyright (C) 2018  Matthieu PETIOT
#
#     https://github.com/ardeidae/tasks-counter
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

"""Tasks counter user interface."""

import datetime

from PyQt5.QtCore import (QByteArray, QFile, QItemSelectionModel, QMimeData,
                          QStringListModel, Qt, QTime, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import (QBrush, QClipboard, QColor, QFont, QIcon, QPalette,
                         QTextCursor, QTextOption)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QColorDialog,
                             QCompleter, QDesktopWidget, QDialog,
                             QDialogButtonBox, QFrame, QGridLayout,
                             QHeaderView, QItemDelegate, QLabel, QLCDNumber,
                             QMainWindow, QPushButton, QSpinBox, QTableView,
                             QTabWidget, QTextBrowser, QTextEdit, QTimeEdit,
                             QToolBar, QVBoxLayout, QWidget, qApp)

import resources
from counter import (Column, ResultColumn, ResultSummaryModel, SettingWrapper,
                     WeekDay, WeekWrapper, color_between,
                     get_last_unique_task_names, minutes_to_time_str,
                     weekday_from_date, weeks_for_year)
from database import close_database
from settings import CELL_HIGHLIGHT_COLOR, CELL_HIGHLIGHT_TEXT_COLOR
from version import author, github_repository, version


class LineEdit(QTextEdit):
    """Custom LineEdit."""

    return_pressed = pyqtSignal()

    def __init__(self, parent=None):
        """Construct a custom line edit."""
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setUndoRedoEnabled(False)
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.completer = None
        self.textChanged.connect(self.__text_has_changed__)

    def set_completer(self, completer):
        """Set the completer on the editor."""
        if completer:
            completer.setWidget(self)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setModelSorting(
                QCompleter.CaseSensitivelySortedModel)
            completer.setMaxVisibleItems(15)
            completer.activated.connect(self.__insert_completion__)
            self.completer = completer

    @pyqtSlot(str)
    def __insert_completion__(self, completion):
        """When the completer is activated, inserts the completion."""
        if self.completer and self.completer.widget() == self:
            self.completer.widget().setPlainText(completion)
            self.completer.widget().moveCursor(QTextCursor.EndOfLine)
            self.completer.widget().ensureCursorVisible()

    def keyPressEvent(self, event):
        """When a key is pressed."""
        if self.completer and self.completer.popup().isVisible():

            if event.key() in (Qt.Key_Return, Qt.Key_Enter,
                               Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Escape):
                event.ignore()
                return
        else:
            if event.key() in(Qt.Key_Return, Qt.Key_Enter):
                self.return_pressed.emit()
                return

        super().keyPressEvent(event)

        if not self.toPlainText():
            self.completer.popup().hide()
            return

        self.completer.setCompletionPrefix(self.toPlainText())
        self.completer.popup().setCurrentIndex(
            self.completer.completionModel().index(0, 0))
        self.completer.complete()

    @pyqtSlot()
    def __text_has_changed__(self):
        """When the text has changed."""
        # remove new lines and strip left blank characters
        self.blockSignals(True)
        cursor_position = self.textCursor().position()

        origin = self.toPlainText()
        # count first whitespaces
        whitespaces = len(origin) - len(origin.lstrip())

        self.setPlainText(' '.join(origin.splitlines()).lstrip())
        cursor = self.textCursor()
        # to avoid offset when setting cursor position, substract whitespaces.
        cursor.setPosition(max(cursor_position - whitespaces, 0))
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self.blockSignals(False)


class TaskNameDelegate(QItemDelegate):
    """Delegate with completion for the task name."""

    def __init__(self, parent):
        """Construct a task name delegate."""
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        """Return the widget used to edit the item specified by index."""
        completer = QCompleter(self)
        string_list_model = QStringListModel(
            get_last_unique_task_names(), completer)
        completer.setModel(string_list_model)
        editor = LineEdit(parent)
        editor.set_completer(completer)
        editor.return_pressed.connect(self.__commit_and_close_editor__)
        return editor

    @pyqtSlot()
    def __commit_and_close_editor__(self):
        """Commit changes and close the editor."""
        editor = self.sender()

        # remove left and right whitespace.
        text = editor.toPlainText()
        editor.setPlainText(' '.join(text.splitlines()).strip())

        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def setEditorData(self, editor, index):
        """Set the data to be displayed and edited.

        Set the data to be displayed and edited by the editor from the
        data model item specified by the model index.
        """
        if editor:
            row = index.row()
            column = index.column()
            try:
                editor.setText(index.model()
                               .get_cached_data(row,
                                                Column(column)))
                editor.selectAll()
            except KeyError:
                print('>>> KeyError')
                pass

    def setModelData(self, editor, model, index):
        """Get data from the editor widget and store it.

        Get data from the editor widget and store it in the specified
        model at the item index.
        """
        if editor:
            model.setData(index, editor.toPlainText(), Qt.EditRole)


class CenterMixin:
    """This mixin allows the centering of window."""

    def center(self):
        """Center the window."""
        if isinstance(self, QWidget):
            geometry = self.frameGeometry()
            center = QDesktopWidget().availableGeometry().center()
            geometry.moveCenter(center)
            self.move(geometry.topLeft())


class SettingsDialog(CenterMixin, QDialog):
    """Settings dialog."""

    def __init__(self, parent=None):
        """Construct a settings dialog."""
        super().__init__(parent)
        self.setWindowTitle('Edit preferences')
        self.center()

        self.invalid_color = None
        self.valid_color = None

        self.__update_colors__()

        manday_time_label = QLabel('Default man day time', self)
        self.manday_time = QTimeEdit(
            SettingWrapper.default_manday_time(), self)
        self.manday_time.timeChanged.connect(
            self.__manday_time_changed__)

        invalid_color_label = QLabel('Invalid color', self)
        self.invalid_color_button = QPushButton(self)
        self.invalid_color_button.clicked.connect(
            self.__open_invalid_color_dialog__)

        valid_color_label = QLabel('Valid color', self)
        self.valid_color_button = QPushButton(self)
        self.valid_color_button.clicked.connect(
            self.__open_valid_color_dialog__)

        self.__update_buttons_colors__()

        main_layout = QGridLayout()

        main_layout.addWidget(manday_time_label, 0, 0)
        main_layout.addWidget(self.manday_time, 0, 1)

        main_layout.addWidget(invalid_color_label, 1, 0)
        main_layout.addWidget(self.invalid_color_button, 1, 1)

        main_layout.addWidget(valid_color_label, 2, 0)
        main_layout.addWidget(self.valid_color_button, 2, 1)

        self.setLayout(main_layout)

    @pyqtSlot()
    def __manday_time_changed__(self):
        """Update the man day time setting."""
        SettingWrapper.set_default_manday_time(self.manday_time.time())

    @pyqtSlot()
    def __open_invalid_color_dialog__(self):
        """Update the invalid color setting."""
        color = QColorDialog.getColor(self.invalid_color, self,
                                      'Select invalid color',
                                      QColorDialog.DontUseNativeDialog)
        if color.isValid():
            SettingWrapper.set_invalid_color(color)

        self.__update_colors__()
        self.__update_buttons_colors__()

    @pyqtSlot()
    def __open_valid_color_dialog__(self):
        """Update the valid color setting."""
        color = QColorDialog.getColor(self.valid_color, self,
                                      'Select invalid color',
                                      QColorDialog.DontUseNativeDialog)
        if color.isValid():
            SettingWrapper.set_valid_color(color)

        self.__update_colors__()
        self.__update_buttons_colors__()

    def __update_colors__(self):
        """Update the local colors values."""
        self.invalid_color = SettingWrapper.invalid_color()
        self.valid_color = SettingWrapper.valid_color()

    def __update_buttons_colors__(self):
        """Update the buttons colors."""
        self.invalid_color_button.setStyleSheet('background-color: {}'
                                                .format(
                                                    self.invalid_color.name())
                                                )
        self.valid_color_button.setStyleSheet('background-color: {}'
                                              .format(
                                                  self.valid_color.name())
                                              )


class AboutDialog(CenterMixin, QDialog):
    """Application about dialog."""

    def __init__(self, parent=None):
        """Construct an about dialog."""
        super().__init__(parent)
        self.setWindowTitle('About this software')
        self.setMinimumHeight(600)
        self.setMinimumWidth(600)
        self.center()

        self.license = self.__build_text_browser__()
        self.about = self.__build_text_browser__()

        repository_label = QLabel(
            '<html>Source repository URL: <a href="{link}">{link}</a></html>'
            .format(link=github_repository), self)
        repository_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        repository_label.setOpenExternalLinks(True)
        author_label = QLabel('Author: {}'.format(author))
        version_label = QLabel(
            'Version: {}'.format(version), self)

        self.tab_widget = QTabWidget(self)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(repository_label)
        layout.addWidget(author_label)
        layout.addWidget(version_label)
        layout.addWidget(self.tab_widget)

        self.tab_widget.addTab(self.license, 'License')
        self.tab_widget.addTab(self.about, 'Third-Party Software Notices')

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.license.setText(self.__get_file_content__(':/LICENSE'))
        self.about.setText(self.__get_file_content__(':/ABOUT'))

    def __build_text_browser__(self):
        """Build a text browser."""
        edit = QTextBrowser()
        edit.setReadOnly(True)
        edit.setOpenExternalLinks(True)
        font = QFont('Courier')
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(11)
        font.setFixedPitch(True)
        edit.setFont(font)
        return edit

    def __get_file_content__(self, resource_file):
        """Get the content of a given resource file."""
        file = QFile(resource_file)
        if file.open(QFile.ReadOnly):
            string = str(file.readAll(), 'utf-8')
            file.close()
            return str(string)
        else:
            print('>>> ' + file.errorString())
            return ''


class MainWindow(QMainWindow):
    """The main window of the application."""

    def __init__(self):
        """Construct a MainWindow."""
        super().__init__()
        self.day_actions = dict()
        self.task_model = None
        self.task_view = None
        self.result_view = None
        self.result_model = ResultSummaryModel()
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

    def __disable_headers_click__(self, _table):
        """Disable click on table headers."""
        _table.horizontalHeader().setSectionsClickable(False)
        _table.setCornerButtonEnabled(False)
        _table.verticalHeader().setSectionsClickable(False)

    def __init_table_view__(self):
        """Create table view and initialize some settings."""
        table = QTableView(self)
        palette = table.palette()
        palette.setBrush(QPalette.Highlight,
                         QBrush(QColor(CELL_HIGHLIGHT_COLOR)))
        palette.setBrush(QPalette.HighlightedText,
                         QBrush(QColor(CELL_HIGHLIGHT_TEXT_COLOR)))
        table.setPalette(palette)
        self.__disable_headers_click__(table)

        return table

    def __set_task_delegate__(self, _table):
        """Set a task delegate on a table."""
        delegate = TaskNameDelegate(_table)
        _table.setItemDelegateForColumn(
            Column.Task.value, delegate)

    def __resize_task_headers__(self):
        """Resize task headers."""
        self.task_view.hideColumn(Column.Id.value)
        self.task_view.horizontalHeader().setSectionResizeMode(
            Column.Task.value,
            QHeaderView.Stretch)
        self.task_view.horizontalHeader().setSectionResizeMode(
            Column.Start_Time.value,
            QHeaderView.Fixed)
        self.task_view.horizontalHeader().resizeSection(
            Column.Start_Time.value, 70)

        self.task_view.horizontalHeader().setSectionResizeMode(
            Column.End_Time.value, QHeaderView.Fixed)
        self.task_view.horizontalHeader().resizeSection(Column.End_Time.value,
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

    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle('Tasks counter')
        self.setWindowIcon(QIcon(':/tasks.png'))
        self.statusBar()

        self.__set_window_size__()
        self.__create_toolbars_and_menus__()
        self.task_view = self.__init_table_view__()
        self.task_view.setSelectionMode(QTableView.SingleSelection)
        self.__set_task_delegate__(self.task_view)
        self.result_view = self.__init_table_view__()
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

        self.manday_tedit = QTimeEdit(SettingWrapper.default_manday_time(),
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
        """Validate the week and the year and update a WeekWrapper."""
        self.week_wrapper = WeekWrapper(
            self.year_edit.value(), self.week_edit.value())

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
        settings = SettingsDialog(self)
        settings.exec_()

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

    @pyqtSlot(int)
    def __week_changed__(self, week):
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
            self.__change_catch_up_color__(SettingWrapper.valid_color())
            self.catch_up_lcdnumber.setToolTip('+' + time_str)
        else:
            self.__change_catch_up_color__(SettingWrapper.invalid_color())
            self.catch_up_lcdnumber.setToolTip('-' + time_str)

        if abs_time >= 6000:
            self.catch_up_lcdnumber.display(abs_time // 60)
        else:
            self.catch_up_lcdnumber.display(time_str)

    def __build_lcd_number_widget__(self):
        """Build a LCD Number widget."""
        lcdnumber = QLCDNumber(self)
        lcdnumber.setSegmentStyle(QLCDNumber.Flat)
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

        color = color_between(SettingWrapper.invalid_color().name(),
                              SettingWrapper.valid_color().name(), percent)
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
