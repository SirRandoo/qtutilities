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
import functools
from typing import Optional, Union

from PySide6 import QtCore, QtWidgets, QtGui

__all__ = ['HelpPage']


class HelpPage(QtWidgets.QWidget):
    """A widget that houses a documentation page."""
    anchor_clicked = QtCore.Signal(QtCore.QUrl)

    def __init__(self, *, parent: QtWidgets.QWidget = None):
        super(HelpPage, self).__init__(parent=parent)

        self.container: Optional[QtWidgets.QWidget] = None
        self.display: Optional[QtWidgets.QTextBrowser] = None

        self.find_flags: Optional[QtWidgets.QGroupBox] = None
        self.find_next_button: Optional[QtWidgets.QToolButton] = None
        self.find_input: Optional[QtWidgets.QLineEdit] = None
        self.find_previous_button: Optional[QtWidgets.QToolButton] = None
        self.find_sensitive: Optional[QtWidgets.QCheckBox] = None
        self.find_words: Optional[QtWidgets.QCheckBox] = None
        self.find_regex: Optional[QtWidgets.QCheckBox] = None

        self.hide_finder_action: Optional[QtGui.QAction] = None
        self.find_next_action: Optional[QtGui.QAction] = None
        self.find_previous_action: Optional[QtGui.QAction] = None
        self.show_finder_action: Optional[QtGui.QAction] = None

    def setup_ui(self):
        """Sets up the page's UI."""
        self.container = QtWidgets.QWidget()

        self.display = QtWidgets.QTextBrowser()
        self.display.anchorClicked.connect(self.anchor_clicked)

        self.find_flags = QtWidgets.QGroupBox('Flags')

        self.find_next_button = QtWidgets.QToolButton()
        self.find_next_button.set_text('➡')
        self.find_next_button.triggered.connect(self.search)

        self.find_input = QtWidgets.QLineEdit()
        self.find_input.setClearButtonEnabled(True)

        self.find_previous_button = QtWidgets.QToolButton()
        self.find_previous_button.set_text('⬅')
        self.find_previous_button.triggered.connect(functools.partial(self.search, previous=True))

        self.find_sensitive = QtWidgets.QCheckBox('Match Case')

        self.find_words = QtWidgets.QCheckBox('Words')

        self.find_regex = QtWidgets.QCheckBox('Regex')
        self.find_regex.clicked.connect(self.handle_regex)

        self.find_previous_action = QtGui.QAction('Find previous...')
        self.find_previous_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Shift, QtCore.Qt.Key_Enter))
        self.find_previous_action.triggered.connect(self.find_previous_button.click)

        self.find_next_action = QtGui.QAction('Find next...')
        self.find_next_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter))
        self.find_next_action.triggered.connect(self.find_next_button.click)

        self.hide_finder_action = QtGui.QAction('Hide')
        self.hide_finder_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape))
        self.hide_finder_action.triggered.connect(self.container.hide)

        self.show_finder_action = QtGui.QAction('Find...')
        self.show_finder_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Control, QtCore.Qt.Key_F))
        self.show_finder_action.triggered.connect(self.container.show)

        page_layout: QtWidgets.QVBoxLayout = self.layout()
        find_layout: QtWidgets.QGridLayout = self.container.layout()
        flag_layout: QtWidgets.QHBoxLayout = self.find_flags.layout()

        if page_layout is None:
            page_layout = QtWidgets.QVBoxLayout(self)

        if find_layout is None:
            find_layout = QtWidgets.QGridLayout(self.container)

        if flag_layout is None:
            flag_layout = QtWidgets.QHBoxLayout(self.find_flags)

        if page_layout.indexOf(self.container) == -1:
            page_layout.insertWidget(0, self.container)

        if page_layout.indexOf(self.display) == -1:
            page_layout.addWidget(self.display)

        if find_layout.indexOf(self.find_previous_button) == -1:
            find_layout.addWidget(self.find_previous_button, 0, 0)

        if find_layout.indexOf(self.find_input) == -1:
            find_layout.addWidget(self.find_input, 0, 1)

        if find_layout.indexOf(self.find_next_button) == -1:
            find_layout.addWidget(self.find_next_button, 0, 2)

        if find_layout.indexOf(self.find_flags) == -1:
            # noinspection PyTypeChecker
            find_layout.addWidget(self.find_flags, 1, 0, -1, -1, 0)

        if flag_layout.indexOf(self.find_sensitive) == -1:
            flag_layout.insertWidget(0, self.find_sensitive)

        if flag_layout.indexOf(self.find_words) == -1:
            flag_layout.insertWidget(1, self.find_words)

        if flag_layout.indexOf(self.find_regex) == -1:
            flag_layout.addWidget(self.find_regex)

        self.find_input.addActions([self.find_previous_action, self.find_next_action, self.hide_finder_action])

        self.display.addAction(self.show_finder_action)

    def set_html(self, html: str):
        """Sets the HTML for the QTextBrowser."""
        self.display.setHtml(html)

    def set_text(self, text: str):
        """Sets the text for the QTextBrowser."""
        self.display.set_text(text)

    def set_plain_text(self, text: str):
        """Sets the plain text for the QTextBrowser."""
        self.display.setPlainText(text)

    def search(self, *args, previous: bool = None):
        """Finds the user's specified query, but backwards."""
        query = self.find_input.text()  # Get the user's query
        doc = self.display.document()  # Get the page's QTextDocument instance

        method: Union[str, QtCore.QRegularExpression] = query

        # Regex check
        if self.find_regex.isChecked():
            method = QtCore.QRegularExpression(query)

            if self.find_sensitive.isChecked():
                method.setCaseSensitivity(QtCore.Qt.CaseSensitive)

            else:
                method.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        flags = 0

        if previous:
            flags = doc.FindBackward

        if self.find_sensitive.isChecked():
            flags = flags | doc.FindCaseSensitively

        if self.find_words.isChecked() and self.find_words.isEnabled():
            flags = flags | doc.FindWholeWords

        cursor = doc.find(method, self.display.cursor(), flags)

        if cursor is not None:
            self.display.setCursor(cursor)

    def handle_regex(self):
        """Updates the flag checkboxes to reflect the user's options when regex
        is enabled/disabled."""
        self.find_words.setDisabled(self.find_regex.isChecked())
