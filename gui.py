"""Tasks counter user interface."""

import datetime
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPalette
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication,
                             QDesktopWidget, QHeaderView, QMainWindow,
                             QMessageBox, QSpinBox, QTableView, QToolBar)

import resources
from counter import Column, WeekDay, WeekWrapper, weekday_from_date


class MainWindow(QMainWindow):
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

    def __center__(self):
        """Center the window."""
        geometry = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(center)
        self.move(geometry.topLeft())

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

    def initUI(self):
        """Initializes the user interface."""
        self.setWindowTitle('Tasks counter')
        self.setWindowIcon(QIcon(':/tasks.png'))
        self.statusBar()

        self.__set_window_size__()
        self.__center__()
        self.__create_toolbars__()
        self.__init_table__()
        self.setCentralWidget(self.table)

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

        previousAct = QAction(QIcon(':/previous.png'), 'Previous', self)
        previousAct.setEnabled(False)
        previousAct.triggered.connect(self.__previous_week__)

        nextAct = QAction(QIcon(':/next.png'), 'Next', self)
        nextAct.setEnabled(False)
        nextAct.triggered.connect(self.__next_week__)

        exitAct = QAction(QIcon(':/exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        self.toolbar_other.addAction(exitAct)
        self.week_edit = QSpinBox()
        self.week_edit.setPrefix('Week: ')
        self.week_edit.setMinimum(1)
        self.week_edit.setMaximum(55)
        self.week_edit.setValue(datetime.date.today().isocalendar()[1])

        self.year_edit = QSpinBox()
        self.year_edit.setPrefix('Year: ')
        self.year_edit.setMinimum(2010)
        self.year_edit.setMaximum(2050)
        self.year_edit.setValue(datetime.datetime.now().year)

        self.week_edit.valueChanged.connect(self.__week_changed__)
        self.year_edit.valueChanged.connect(self.__year_changed__)

        self.toolbar_other.addWidget(self.year_edit)
        self.toolbar_other.addWidget(self.week_edit)

        self.toolbar_other.addAction(previousAct)
        self.toolbar_other.addAction(nextAct)

    def __validate_week_and_year__(self):
        """Validates the week and the year and updates a WeekWrapper."""
        print('validate week and year')
        # TODO: check values
        print(self.year_edit.value())
        print(self.week_edit.value())

        print('>>> create week wrapper')
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
        print('previous week')

    def __next_week__(self):
        """The next week button was clicked."""
        print('next week')

    def __change_current_day__(self):
        """Changes the current day for edition."""
        sender = self.sender()
        print(sender.text() + ' clicked')
        if self.week_wrapper:
            print(WeekDay[sender.text()])
            self.model = self.week_wrapper[WeekDay[sender.text()]]
            print(self.model)
            self.table.setModel(self.model)

            self.__resize_headers__()

    def __year_changed__(self, year):
        """The current year has changed."""
        print('Year: ' + str(year))
        # TODO: update week number max value for this year

    def __week_changed__(self, week):
        """The current week has changed."""
        print('Week: ' + str(week))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = MainWindow()
    mw.initUI()

    sys.exit(app.exec_())
