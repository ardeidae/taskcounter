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

from PyQt5.QtCore import (QFile, QItemSelectionModel, QStringListModel, Qt,
                          pyqtSignal)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QPalette, QTextCursor,
                         QTextOption)
from PyQt5.QtWidgets import (QAction, QActionGroup, QCompleter, QDesktopWidget,
                             QDialog, QDialogButtonBox, QFrame, QGridLayout,
                             QHeaderView, QItemDelegate, QLabel, QLCDNumber,
                             QMainWindow, QSpinBox, QTableView, QTabWidget,
                             QTextBrowser, QTextEdit, QToolBar, QVBoxLayout,
                             QWidget)

import resources
from counter import (Column, WeekDay, WeekWrapper, get_last_unique_task_names,
                     minutes_to_time_str, weekday_from_date, weeks_for_year)
from database import close_database, create_database
from version import author, github_repository, version


class LineEdit(QTextEdit):
    """Custom LineEdit."""

    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        """Constructs a custom line edit."""
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
        """Sets the completer on the editor."""
        if completer:
            completer.setWidget(self)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setModelSorting(
                QCompleter.CaseSensitivelySortedModel)
            completer.setMaxVisibleItems(15)
            completer.activated.connect(self.__insert_completion__)
            self.completer = completer

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
                self.returnPressed.emit()
                return

        super().keyPressEvent(event)

        if not self.toPlainText():
            self.completer.popup().hide()
            return

        self.completer.setCompletionPrefix(self.toPlainText())
        self.completer.popup().setCurrentIndex(
            self.completer.completionModel().index(0, 0))
        self.completer.complete()

    def __text_has_changed__(self):
        """When the text has changed."""
        # remove new lines and strip left blank characters
        self.blockSignals(True)
        cursor = self.textCursor()
        self.setPlainText(' '.join(self.toPlainText().splitlines()).lstrip())
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self.blockSignals(False)


class TaskNameDelegate(QItemDelegate):
    """Delegate with completion for the task name."""

    def __init__(self, parent):
        """Constructs a task name delegate."""
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        """Returns the widget used to edit the item specified by index."""
        completer = QCompleter(self)
        string_list_model = QStringListModel(
            get_last_unique_task_names(), completer)
        completer.setModel(string_list_model)
        editor = LineEdit(parent)
        editor.set_completer(completer)
        editor.returnPressed.connect(self.__commit_and_close_editor__)
        return editor

    def __commit_and_close_editor__(self):
        """Commits changes and closes the editor."""
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def setEditorData(self, editor, index):
        """Sets the data to be displayed and edited by the editor from the
        data model item specified by the model index."""
        if editor:
            row = index.row()
            column = index.column()
            try:
                editor.setText(index.model().data[row][Column(column)])
                editor.selectAll()
            except KeyError:
                print('>>> KeyError')
                pass

    def setModelData(self, editor, model, index):
        """Gets data from the editor widget and stores it in the specified
        model at the item index."""
        if editor:
            model.setData(index, editor.toPlainText(), Qt.EditRole)


class CenterMixin:
    """This mixin allows the centering of window."""

    def center(self):
        """Centers the window."""
        geometry = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(center)
        self.move(geometry.topLeft())


class About(CenterMixin, QDialog):
    """Application about dialog."""

    def __init__(self, parent=None):
        """Constructs an about dialog."""
        super().__init__(parent)
        self.setWindowTitle('About this software')
        self.setMinimumHeight(600)
        self.setMinimumWidth(600)
        self.setMaximumHeight(600)
        self.setMaximumWidth(600)
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
        """Builds a text browser."""
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
        """Gets the content of a given resource file."""
        file = QFile(resource_file)
        if file.open(QFile.ReadOnly):
            string = str(file.readAll(), 'utf-8')
            file.close()
            return str(string)
        else:
            print('>>> ' + file.errorString())
            return ''


class MainWindow(CenterMixin, QMainWindow):
    """The main window of the application."""

    def __init__(self):
        """Constructs a MainWindow."""
        super().__init__()
        self.dayActions = dict()
        self.model = None
        self.table = None
        self.toolbar_days = None
        self.toolbar_other = None
        self.week_edit = None
        self.week_wrapper = None
        self.year_edit = None
        self.current_day_label = None
        self.week_time_lcdnumber = None
        self.day_time_lcdnumber = None

    def closeEvent(self, event):
        """When application is about to close."""
        close_database()

    def __set_window_size__(self):
        """Sets the window size."""
        self.setMinimumHeight(600)
        self.setMinimumWidth(600)
        self.setMaximumHeight(600)
        self.setMaximumWidth(600)

    def __disable_headers_click__(self):
        """Disables click on table headers."""
        self.table.horizontalHeader().setSectionsClickable(False)
        self.table.setCornerButtonEnabled(False)
        self.table.verticalHeader().setSectionsClickable(False)

    def __init_table__(self):
        """Creates table view and initializes some settings."""
        self.table = QTableView()
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        palette = self.table.palette()
        palette.setBrush(QPalette.Highlight, QBrush(QColor('#fffd88')))
        palette.setBrush(QPalette.HighlightedText, QBrush(Qt.red))
        self.table.setPalette(palette)
        self.__disable_headers_click__()
        task_name_delegate = TaskNameDelegate(self.table)
        self.table.setItemDelegateForColumn(
            Column.Task.value, task_name_delegate)

    def __resize_headers__(self):
        """Resizes headers."""
        self.table.hideColumn(Column.Id.value)
        self.table.horizontalHeader() \
            .setSectionResizeMode(Column.Task.value,
                                  QHeaderView.Stretch)
        self.table.horizontalHeader() \
            .setSectionResizeMode(Column.Start_Time.value,
                                  QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(Column.Start_Time.value,
                                                    70)

        self.table.horizontalHeader() \
            .setSectionResizeMode(Column.End_Time.value,
                                  QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(Column.End_Time.value, 70)

    def __init_layout__(self):
        """Initializes the central widget layout."""
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.current_day_label = QLabel('', self)
        self.current_day_label.setAlignment(Qt.AlignCenter)
        self.current_day_label.setMargin(5)
        title_font = self.current_day_label.font()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.current_day_label.setFont(title_font)
        main_layout.addWidget(self.current_day_label)
        main_layout.addWidget(self.table)

        week_label = QLabel("Week time")
        self.week_time_lcdnumber = self.__build_lcd_number_widget__()
        self.__change_week_color__(Qt.darkBlue)

        day_label = QLabel("Day time")
        self.day_time_lcdnumber = self.__build_lcd_number_widget__()
        self.__change_day_color__(Qt.darkGreen)

        footer_layout = QGridLayout()
        footer_layout.addWidget(day_label, 0, 0,
                                Qt.AlignHCenter | Qt.AlignVCenter)
        footer_layout.addWidget(week_label, 0, 1,
                                Qt.AlignHCenter | Qt.AlignVCenter)
        footer_layout.addWidget(self.day_time_lcdnumber, 1, 0,
                                Qt.AlignHCenter | Qt.AlignVCenter)
        footer_layout.addWidget(self.week_time_lcdnumber, 1, 1,
                                Qt.AlignHCenter | Qt.AlignVCenter)

        main_layout.addLayout(footer_layout)

        main_widget.setLayout(main_layout)

    def __set_day_title__(self, title):
        """Sets the day title on top of the table view."""
        self.current_day_label.setText(str(title))

    def __change_week_color__(self, color):
        """Changes the lcd week color."""
        self.__change_lcd_number_color__(self.week_time_lcdnumber, color)

    def __change_day_color__(self, color):
        """Changes the lcd day color."""
        self.__change_lcd_number_color__(self.day_time_lcdnumber, color)

    def __change_lcd_number_color__(self, lcd_widget, color):
        """Changes a given lcd number color with a given color."""
        if isinstance(color, Qt.GlobalColor) and isinstance(lcd_widget,
                                                            QLCDNumber):
            palette = QPalette()
            palette.setColor(QPalette.WindowText, color)
            lcd_widget.setPalette(palette)

    def initUI(self):
        """Initializes the user interface."""
        self.setWindowTitle('Tasks counter')
        self.setWindowIcon(QIcon(':/tasks.png'))
        self.statusBar()

        self.__set_window_size__()
        self.center()
        self.__create_toolbars__()
        self.__init_table__()
        self.__init_layout__()

        self.__validate_week_and_year__()

        self.show()

    def __create_toolbars__(self):
        """Creates the toolbars."""
        self.toolbar_other = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar_other)
        self.addToolBarBreak()
        self.toolbar_days = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar_days)

        daysActionGroup = QActionGroup(self)
        for day in WeekDay:
            action = QAction(
                QIcon(':/' + day.name.lower() + '.png'), day.name, self)
            action.setCheckable(True)
            action.setStatusTip('Go to ' + day.name)
            action.triggered.connect(self.__change_current_day__)
            daysActionGroup.addAction(action)
            self.dayActions[day] = action
            self.toolbar_days.addAction(action)

        previousAct = QAction(QIcon(':/previous.png'), 'Previous Week', self)
        previousAct.triggered.connect(self.__previous_week__)
        previousAct.setStatusTip('Go to Previous Week')

        nextAct = QAction(QIcon(':/next.png'), 'Next Week', self)
        nextAct.triggered.connect(self.__next_week__)
        nextAct.setStatusTip('Go to Next Week')

        todayAct = QAction(QIcon(':/today.png'), 'Today', self)
        todayAct.triggered.connect(self.__today__)
        todayAct.setStatusTip('Go to today')

        aboutAct = QAction(QIcon(':/info.png'), 'About', self)
        aboutAct.triggered.connect(self.__about__)
        aboutAct.setStatusTip('About this application')

        exitAct = QAction(QIcon(':/exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
        self.toolbar_other.addAction(exitAct)

        self.year_edit = QSpinBox()
        self.year_edit.setPrefix('Year: ')
        self.year_edit.setMinimum(2010)
        self.year_edit.setMaximum(2050)
        self.year_edit.setValue(datetime.datetime.now().year)

        self.week_edit = QSpinBox()
        self.week_edit.setPrefix('Week: ')
        self.week_edit.setMinimum(1)
        self.__update_week_edit__(self.year_edit.value())
        self.week_edit.setValue(datetime.date.today().isocalendar()[1])

        self.week_edit.valueChanged.connect(self.__week_changed__)
        self.year_edit.valueChanged.connect(self.__year_changed__)

        self.toolbar_other.addWidget(self.year_edit)
        self.toolbar_other.addWidget(self.week_edit)

        self.toolbar_other.addAction(previousAct)
        self.toolbar_other.addAction(nextAct)
        self.toolbar_other.addAction(todayAct)
        self.toolbar_other.addAction(aboutAct)

    def __validate_week_and_year__(self):
        """Validates the week and the year and updates a WeekWrapper."""
        self.week_wrapper = WeekWrapper(
            self.year_edit.value(), self.week_edit.value())

        if (self.year_edit.value() == datetime.datetime.now().year
                and self.week_edit.value() ==
                datetime.date.today().isocalendar()[1]):
            self.dayActions[weekday_from_date(
                datetime.date.today())].activate(QAction.Trigger)
        else:
            self.dayActions[WeekDay.Monday].activate(QAction.Trigger)

    def __previous_week__(self):
        """The previous week button was clicked."""
        current_week = int(self.week_edit.value())
        if current_week - 1 == 0:
            current_year = int(self.year_edit.value())
            weeks_of_previous_year = weeks_for_year(current_year - 1)
            self.week_edit.setValue(weeks_of_previous_year)
            self.year_edit.setValue(current_year - 1)
        else:
            self.week_edit.setValue(current_week - 1)

    def __next_week__(self):
        """The next week button was clicked."""
        current_week = int(self.week_edit.value())
        current_year = int(self.year_edit.value())
        weeks_of_current_year = weeks_for_year(current_year)
        if current_week + 1 > weeks_of_current_year:
            self.week_edit.setValue(1)
            self.year_edit.setValue(current_year + 1)
        else:
            self.week_edit.setValue(current_week + 1)

    def __today__(self):
        """The today button was clicked."""
        self.year_edit.setValue(datetime.datetime.now().year)
        self.__update_week_edit__(self.year_edit.value())
        self.week_edit.setValue(datetime.date.today().isocalendar()[1])
        self.__validate_week_and_year__()

    def __about__(self):
        """The about button was clicked."""
        about = About(self)
        about.exec_()

    def __change_current_day__(self):
        """Changes the current day for edition."""
        sender = self.sender()
        if self.week_wrapper:
            if self.model:
                self.model.dataChanged.disconnect()
            self.model = self.week_wrapper[WeekDay[sender.text()]]
            self.__update_day_time_counter__()
            self.__update_week_time_counter__()
            self.model.dataChanged.connect(
                self.__update_day_time_counter__)
            self.model.dataChanged.connect(
                self.__update_week_time_counter__)

            # set readable date in title
            self.__set_day_title__(self.model.date.strftime('%A %d %B %Y'))
            self.table.setModel(self.model)

            self.__resize_headers__()

            # the table takes the focus
            self.table.setFocus(Qt.OtherFocusReason)

            # the last task cell is selected
            flags = QItemSelectionModel.ClearAndSelect
            index = self.model.last_task_cell_index
            self.table.selectionModel().setCurrentIndex(index, flags)

    def __year_changed__(self, year):
        """The current year has changed."""
        self.__update_week_edit__(year)
        self.__validate_week_and_year__()

    def __week_changed__(self, week):
        """The current week has changed."""
        self.__validate_week_and_year__()

    def __update_week_edit__(self, year):
        """Updates the week edit max value for a given year."""
        weeks = weeks_for_year(int(year))
        self.week_edit.setMaximum(weeks)

    def __update_day_time_counter__(self):
        """Updates the day time counter."""
        self.day_time_lcdnumber.display(
            minutes_to_time_str(self.model.minutes_of_day))

    def __update_week_time_counter__(self):
        """Updates the week time counter."""
        self.week_time_lcdnumber.display(
            minutes_to_time_str(self.week_wrapper.minutes_of_week))

    def __build_lcd_number_widget__(self):
        """Builds a LCD Number widget."""
        lcdnumber = QLCDNumber(self)
        lcdnumber.setSegmentStyle(QLCDNumber.Flat)
        lcdnumber.setFixedHeight(40)
        lcdnumber.setFrameStyle(QFrame.NoFrame)
        return lcdnumber
