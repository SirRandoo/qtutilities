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
from PySide6 import QtCore, QtGui, QtWidgets

__all__ = ['QPopoutOverlay']


class QPopoutOverlay(QtWidgets.QWidget):
    """Creates an overlay with a singular button. This overlay is used to define
    "popout-able" widgets."""
    popout_requested = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget = None):
        #  Super Call  #
        super(QPopoutOverlay, self).__init__(parent=parent)

        #  Attributes  #
        self._size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self._size_policy.setHorizontalStretch(0)
        self._size_policy.setVerticalStretch(0)
        self._size_policy.setWidthForHeight(False)

        self._popout = QtWidgets.QPushButton(parent=self)
        self._popout.setText('◹')
        self._popout.setIconSize(QtCore.QSize(8, 8))
        self._popout.setMaximumSize(16, 16)
        self._popout.setFlat(True)
        self._popout.setSizePolicy(self._size_policy)
        self._popout.setStyleSheet('QPushButton:focus {border: none; outline: none;}')

        self._layout = QtWidgets.QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setHorizontalSpacing(0)
        self._layout.setVerticalSpacing(0)

        self._layout.addItem(
            QtWidgets.QSpacerItem(12, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored),
            0, 0
        )
        self._layout.addWidget(self._popout, 0, 1, 1, 1)
        self._layout.addItem(
            QtWidgets.QSpacerItem(0, 12, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding),
            1, 1
        )

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setLayout(self._layout)

        self._popout.clicked.connect(self.popout_requested.emit)

    @property
    def icon(self) -> QtGui.QIcon:
        return self._popout.icon()

    @icon.setter
    def icon(self, value: QtGui.QIcon):
        self._popout.setIcon(value)
        self._popout.setText('◹' if value.isNull() else '')
