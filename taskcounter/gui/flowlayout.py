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

    def __init__(self, parent=None, margin=-1, hSpacing=-1, vSpacing=-1):
        """Construct a Flow Layout."""
        super().__init__(parent)

        self.setContentsMargins(margin, margin, margin, margin)
        self.m_hSpace = hSpacing
        self.m_vSpace = vSpacing

        self.itemList = []

    def __del__(self):
        """Destroy this instance."""
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        """Add an item."""
        self.itemList.append(item)

    def horizontalSpacing(self):
        """Get the horizontal spacing between widgets."""
        if self.m_hSpace >= 0:
            return self.m_hSpace
        else:
            return self.__smartSpacing__(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        """Get the vertical spacing between widgets."""
        if self.m_vSpace >= 0:
            return self.m_vSpace
        else:
            return self.__smartSpacing__(QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        """Return the number of items in the layout."""
        return len(self.itemList)

    def itemAt(self, index):
        """Return the layout item at index."""
        if 0 <= index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        """Remove the layout item at index from the layout, and return it."""
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        """Return whether layout can make use of more space than sizeHint."""
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        """Return true if layout's preferred height depends on its width."""
        return True

    def heightForWidth(self, width):
        """Return preferred height for this layout item, given the width."""
        height = self.__doLayout__(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        """Define the rectangle covered by this layout item."""
        super().setGeometry(rect)
        self.__doLayout__(rect, False)

    def sizeHint(self):
        """Return the preferred size of this item."""
        return self.minimumSize()

    def minimumSize(self):
        """Return the minimum size of this item."""
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        left, top, right, bottom = self.getContentsMargins()

        size += QSize(left + right, top + bottom)
        return size

    def __doLayout__(self, rect, testOnly):
        """Calculate the area available to the layout items."""
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(+left, +top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = wid.style().layoutSpacing(QSizePolicy.PushButton,
                                                   QSizePolicy.PushButton,
                                                   Qt.Horizontal)

            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = wid.style().layoutSpacing(QSizePolicy.PushButton,
                                                   QSizePolicy.PushButton,
                                                   Qt.Vertical)

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y() + bottom

    def __smartSpacing__(self, pm):
        """Get default spacing for either top-level or sub layouts."""
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
