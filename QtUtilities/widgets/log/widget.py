"""
The MIT License (MIT)

Copyright (c) 2021 SirRandoo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

# TODO: Figure out a way to link the QTableWidget to the QLog's record list.
# TODO: Allow for the panels to be collapsible when no longer in use.
# TODO: Allow the user to specify custom colors for the QTableWidget.
#
# TODO: Add a context menu to the QTableWidget that allows users to...
#       - Clear the log
#       - Show details about a record
#
# TODO: Allow for users to filter the log by...
#       - Level
#       - Date
#       - Time
#       - Message content
#       - Function name
#       - Thread name
#       - Logger name
#       - Process name
#       - Path
#       - Module name
import datetime
from typing import Optional, List

from PySide6 import QtCore, QtWidgets, QtGui

from QtUtilities.utils import append_table, set_table_headers

__all__ = ['QLog']


class QLog(QtWidgets.QDialog):
    """A dialog for displaying output from Python's logging module."""

    def __init__(self, *, parent: QtWidgets.QWidget = None):
        super(QLog, self).__init__(parent=parent)

        self.toolbar: Optional[QtWidgets.QToolBar] = None
        self.toolbar_container: Optional[QtWidgets.QStackedWidget] = None
        self.display: Optional[QtWidgets.QTableWidget] = None
        self.details: Optional[QtWidgets.QTableWidget] = None

        self.filter_container: Optional[QtWidgets.QWidget] = None

        self.level_panel: Optional[QtWidgets.QGroupBox] = None
        self.level_filter: Optional[QtWidgets.QListWidget] = None

        self.logger_panel: Optional[QtWidgets.QGroupBox] = None
        self.logger_filter: Optional[QtWidgets.QTreeWidget] = None

        self.filter_action: Optional[QtGui.QAction] = None
        self.color_action: Optional[QtGui.QAction] = None

        self.deselect_action: Optional[QtGui.QAction] = None

        self._records: List[dict] = []

        self.setup_ui()
        self.bind()

    def setup_ui(self):
        """Sets up the dialog's ui."""
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setAllowedAreas(QtCore.Qt.AllToolBarAreas)
        self.toolbar.setFloatable(False)
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.toolbar_container = QtWidgets.QStackedWidget()
        self.toolbar_container.setHidden(True)

        self.display = QtWidgets.QTableWidget()
        self.display.setWordWrap(True)
        self.display.setEditTriggers(self.display.NoEditTriggers)
        self.display.setDropIndicatorShown(False)
        self.display.setDragDropOverwriteMode(False)
        self.display.setSortingEnabled(True)
        self.display.verticalHeader().setHidden(True)

        set_table_headers(self.display, ['Timestamp', 'Name', 'Level', 'Message'])
        append_table(self.display, Timestamp=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
                     Name='root', Level='INFO', Message='Testing')

        self.details = QtWidgets.QTableWidget()
        self.details.setWordWrap(True)
        self.details.setEditTriggers(self.details.NoEditTriggers)
        self.details.setDropIndicatorShown(False)
        self.details.setDragDropOverwriteMode(False)
        self.details.setSortingEnabled(False)
        self.details.verticalHeader().setHidden(True)
        self.details.setHidden(True)

        set_table_headers(self.details, ['Key', 'Value'])

        self.filter_action = QtGui.QAction('⧩')
        self.filter_action.setToolTip('Opens the filter panel.')

        self.color_action = QtGui.QAction('🖌')
        self.color_action.setToolTip('Opens the color panel.')

        self.filter_container = QtWidgets.QWidget()

        self.level_panel = QtWidgets.QGroupBox('Level Filter')
        self.level_panel.setFlat(True)

        self.level_filter = QtWidgets.QListWidget()
        self.level_filter.setEditTriggers(self.level_filter.NoEditTriggers)
        self.level_filter.setWordWrap(True)
        self.level_filter.setDropIndicatorShown(False)
        self.level_filter.setDragDropOverwriteMode(False)
        self.level_filter.setSortingEnabled(True)

        self.logger_panel = QtWidgets.QGroupBox('Logger Filter')
        self.logger_panel.setFlat(True)

        self.logger_filter = QtWidgets.QTreeWidget()
        self.logger_filter.setWordWrap(True)
        self.logger_filter.setEditTriggers(self.logger_filter.NoEditTriggers)
        self.logger_filter.setDropIndicatorShown(False)
        self.logger_filter.setDragEnabled(False)
        self.logger_filter.setSortingEnabled(True)
        self.logger_filter.setDragDropOverwriteMode(False)
        self.logger_filter.setHeaderHidden(True)

        self.deselect_action = QtGui.QAction('Deselect')
        self.deselect_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape))

        layout = QtWidgets.QGridLayout(self)

        layout.addWidget(self.toolbar, 0, 0)
        layout.addWidget(self.toolbar_container, 0, 1)
        layout.addWidget(self.display, 0, 2)
        layout.addWidget(self.details, 1, 2)

        layout.setContentsMargins(5, 5, 5, 5)

        # Toolbar insertion
        self.toolbar.addAction(self.filter_action)
        self.toolbar.addAction(self.color_action)

        # Filter panel
        self.toolbar_container.addWidget(self.filter_container)
        f_layout = QtWidgets.QGridLayout(self.filter_container)

        f_layout.addWidget(self.logger_panel, 0, 0)
        f_layout.addWidget(self.level_panel, 1, 0)

        # Level filter
        f_le_layout = QtWidgets.QGridLayout(self.level_panel)
        f_le_layout.addWidget(self.level_filter)

        # Logger filter
        f_lo_layout = QtWidgets.QGridLayout(self.logger_panel)
        f_lo_layout.addWidget(self.logger_filter)

        # Misc
        self.display.addAction(self.deselect_action)

    def bind(self):
        """Binds the ui's signals to their respective slots."""
        self.display.itemActivated.connect(self.open_detailed_display)
        self.level_filter.itemActivated.connect(self.reset_display_filter)
        self.logger_filter.itemActivated.connect(self.reset_display_filter)
        self.filter_action.triggered.connect(self.toggle_filter_panel)
        self.color_action.triggered.connect(self.toggle_color_panel)
        self.deselect_action.triggered.connect(self.display.clearSelection)

    def open_detailed_display(self, item: QtWidgets.QTableWidgetItem = None):
        """Opens the detailed display for the selected record."""
        if item is None:
            raise ValueError

        raise NotImplementedError

    def reset_display_filter(self):
        raise NotImplementedError

    def toggle_filter_panel(self):
        raise NotImplementedError

    def toggle_color_panel(self):
        raise NotImplementedError


if __name__ == '__main__':
    a = QtWidgets.QApplication([])

    log = QLog()
    log.show()

    a.exec()
