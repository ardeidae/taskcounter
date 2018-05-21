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

"""Task counter task name delegate."""

from PyQt5.QtCore import QStringListModel, Qt, pyqtSlot
from PyQt5.QtWidgets import QCompleter, QItemDelegate

from taskcounter.enum import TaskColumn
from taskcounter.gui.lineedit import LineEdit
from taskcounter.model import get_last_unique_task_names


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
            editor.setText(index.model()
                           .get_cached_data(row,
                                            TaskColumn(column)))
            editor.selectAll()

    def setModelData(self, editor, model, index):
        """Get data from the editor widget and store it.

        Get data from the editor widget and store it in the specified
        model at the item index.
        """
        if editor:
            model.setData(index, editor.toPlainText(), Qt.EditRole)
