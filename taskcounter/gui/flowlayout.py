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

"""Task counter flow layout."""

from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import QLayout, QSizePolicy, QStyle


class FlowLayout(QLayout):
    """Flow Layout implements a layout that handles different window sizes."""

    def __init__(self, parent=None, margin=-1, h_spacing=-1, v_spacing=-1):
        """Construct a Flow Layout."""
        super().__init__(parent)

        self.setContentsMargins(margin, margin, margin, margin)
        self.h_spacing = h_spacing
        self.v_spacing = v_spacing

        self.items = []

    def __del__(self):
        """Destroy this instance."""
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        """Add an item."""
        self.items.append(item)

    def horizontal_spacing(self):
        """Get the horizontal spacing between widgets."""
        if self.h_spacing >= 0:
            return self.h_spacing
        else:
            return self.__smart_spacing(QStyle.PM_LayoutHorizontalSpacing)

    def vertical_spacing(self):
        """Get the vertical spacing between widgets."""
        if self.v_spacing >= 0:
            return self.v_spacing
        else:
            return self.__smart_spacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        """Return the number of items in the layout."""
        return len(self.items)

    def itemAt(self, index):
        """Return the layout item at index."""
        if 0 <= index < len(self.items):
            return self.items[index]

        return None

    def takeAt(self, index):
        """Remove the layout item at index from the layout, and return it."""
        if 0 <= index < len(self.items):
            return self.items.pop(index)

        return None

    def expandingDirections(self):
        """Return whether layout can make use of more space than sizeHint."""
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        """Return true if layout's preferred height depends on its width."""
        return True

    def heightForWidth(self, width):
        """Return preferred height for this layout item, given the width."""
        height = self.__do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        """Define the rectangle covered by this layout item."""
        super().setGeometry(rect)
        self.__do_layout(rect, False)

    def sizeHint(self):
        """Return the preferred size of this item."""
        return self.minimumSize()

    def minimumSize(self):
        """Return the minimum size of this item."""
        size = QSize()

        for item in self.items:
            size = size.expandedTo(item.minimumSize())

        left, top, right, bottom = self.getContentsMargins()

        size += QSize(left + right, top + bottom)
        return size

    def __do_layout(self, rect, test_only):
        """Calculate the area available to the layout items."""
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self.items:
            wid = item.widget()
            space_x = self.horizontal_spacing()
            if space_x == -1:
                space_x = wid.style().layoutSpacing(QSizePolicy.PushButton,
                                                    QSizePolicy.PushButton,
                                                    Qt.Horizontal)

            space_y = self.vertical_spacing()
            if space_y == -1:
                space_y = wid.style().layoutSpacing(QSizePolicy.PushButton,
                                                    QSizePolicy.PushButton,
                                                    Qt.Vertical)

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom

    def __smart_spacing(self, pm):
        """Get default spacing for either top-level or sub layouts."""
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
