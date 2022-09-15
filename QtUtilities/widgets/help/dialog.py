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
import logging
from typing import Optional, Dict

from PySide6 import QtCore, QtGui, QtHelp, QtWidgets

from .page import HelpPage
from ...signals import wait_for_signal

__all__ = ['Help']

logger = logging.getLogger(__name__)


class Help(QtWidgets.QDialog):
    """A dialog for displaying documentation.

    TODO: Tree view of all topics and sub-topics, and maybe documentation headers.
    TODO: Maybe different tabs?
    TODO: Documentation search
    """

    def __init__(self, collection_file: str, parent: QtWidgets.QWidget = None):
        super(Help, self).__init__(parent=parent)

        self.tabs: Optional[QtWidgets.QTabBar] = None
        self.new_tab: Optional[QtWidgets.QToolButton] = None
        self.url_box: Optional[QtWidgets.QLineEdit] = None
        self.back_button: Optional[QtWidgets.QToolButton] = None
        self.forward_button: Optional[QtWidgets.QToolButton] = None
        self.home_button: Optional[QtWidgets.QToolButton] = None
        self.page_container: Optional[QtWidgets.QStackedWidget] = None

        self.url_completer: Optional[QtWidgets.QCompleter] = None
        self.url_validator: Optional[QtGui.QRegularExpressionValidator] = None

        self._engine: QtHelp.QHelpEngineCore = QtHelp.QHelpEngineCore(collection_file)
        self._pages: Dict[str, HelpPage] = {}

    # Ui methods
    def setup_ui(self):
        """Sets up the dialog's UI."""
        self.tabs = QtWidgets.QTabBar()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(QtCore.Qt.ElideRight)
        self.tabs.setUsesScrollButtons(False)
        self.tabs.setExpanding(False)
        self.tabs.setMovable(True)
        self.tabs.setSelectionBehaviorOnRemove(self.tabs.SelectLeftTab)
        self.tabs.setShape(self.tabs.RoundedNorth)

        self.tabs.currentChanged.connect(self.change_page)

        self.new_tab = QtWidgets.QToolButton()
        self.new_tab.set_text('+')
        self.new_tab.setAutoRaise(True)
        self.new_tab.triggered.connect(self.handle_new_tab)

        self.url_box = QtWidgets.QLineEdit()
        self.url_box.setReadOnly(False)
        self.url_box.setClearButtonEnabled(True)
        self.url_box.setPlaceholderText('Search or type a url')

        self.back_button = QtWidgets.QToolButton()
        self.back_button.set_text('◀️')

        self.forward_button = QtWidgets.QToolButton()
        self.forward_button.set_text('▶️')

        self.home_button = QtWidgets.QToolButton()
        self.home_button.set_text('🏠')

        self.page_container = QtWidgets.QStackedWidget()

        self.url_completer = QtWidgets.QCompleter()
        self.url_box.setCompleter(self.url_completer)

        self.url_validator = QtGui.QRegularExpressionValidator()
        self.url_box.setValidator(self.url_validator)

        # Layout validation
        layout: QtWidgets.QGridLayout = self.layout()

        if layout is None:
            layout = QtWidgets.QGridLayout(self)

        # Layout insertion
        if layout.indexOf(self.tabs) == -1:
            layout.addWidget(self.tabs, 0, 0, -1, -1)

        if layout.indexOf(self.back_button) == -1:
            layout.addWidget(self.back_button, 1, 0)

        if layout.indexOf(self.forward_button) == -1:
            layout.addWidget(self.forward_button, 1, 1)

        if layout.indexOf(self.home_button) == -1:
            layout.addWidget(self.home_button, 1, 2)

        if layout.indexOf(self.url_box) == -1:
            layout.addWidget(self.url_box, 1, 3, -1, -1)

        if layout.indexOf(self.page_container) == -1:
            layout.addWidget(self.page_container, 2, 0, -1, -1)

        # QTabBar prep
        if (self.tabs.count() > 0 and self.tabs.isTabEnabled(self.tabs.count() - 1)) or self.tabs.count() <= 0:
            self.tabs.addTab('')
            self.tabs.setTabEnabled(self.tabs.count() - 1, False)
            self.tabs.setTabButton(self.tabs.count() - 1, self.tabs.RightSide, self.new_tab)

        # QHelpEngineCore prepare_ui
        prepare_ui = self._engine.setupData()
        wait_for_signal(self._engine.setupFinished)

        if not prepare_ui:
            logger.warning(f'QHelpEngineCore prepare_ui failed!  ({self._engine.error()})')

        # Ensure there's one tab open
        if self.tabs.count() <= 1:
            self.new_tab.click()

    def change_page(self, index: int):
        """Changes the current visible page to the user's requested page."""
        text = self.tabs.tabText(index)

        if text in self._pages:
            self.page_container.setCurrentWidget(self._pages[text])

        else:
            self.tabs.removeTab(index)

    def handle_new_tab(self):
        """Creates a new tab."""
        self.tabs.insertTab(self.tabs.count() - 2, '')
        self.tabs.setCurrentIndex(self.tabs.count() - 2)
