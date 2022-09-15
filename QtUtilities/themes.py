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

__all__ = ['dark', 'high_contrast']


def dark(app: QtWidgets.QWidget):
    """Transforms the widget's palette into a darker look."""
    palette = QtGui.QPalette()
    qcolor = QtGui.QColor
    white = QtCore.Qt.white
    yellow = QtCore.Qt.yellow
    light_gray = QtCore.Qt.lightGray

    palette.setColor(palette.Window, qcolor(50, 50, 50))
    palette.setColor(palette.WindowText, white)
    palette.setColor(palette.Base, qcolor(90, 90, 90))
    palette.setColor(palette.AlternateBase, qcolor(100, 100, 100))
    palette.setColor(palette.ToolTipBase, qcolor(120, 120, 120))
    palette.setColor(palette.ToolTipText, white)
    palette.setColor(palette.Text, white)
    palette.setColor(palette.Button, qcolor(70, 70, 70))
    palette.setColor(palette.ButtonText, white)
    palette.setColor(palette.BrightText, yellow)
    palette.setColor(palette.Link, QtCore.Qt.cyan)
    palette.setColor(palette.LinkVisited, QtCore.Qt.darkCyan)

    palette.setColor(palette.Disabled, palette.Text, light_gray)
    palette.setColor(palette.Disabled, palette.ButtonText, light_gray)

    app.setPalette(palette)


def high_contrast(app: QtWidgets.QWidget):
    """Transforms the widget's palette into a darker, higher contrast look."""
    palette = QtGui.QPalette()
    qcolor = QtGui.QColor
    yellow: QtGui.QColor = qcolor(QtCore.Qt.yellow)
    dark_yellow: QtGui.QColor = qcolor(QtCore.Qt.darkYellow)
    light_yellow: QtGui.QColor = yellow.lighter()

    palette.setColor(palette.Window, qcolor(10, 10, 10))
    palette.setColor(palette.WindowText, yellow)
    palette.setColor(palette.Base, qcolor(50, 50, 50))
    palette.setColor(palette.AlternateBase, qcolor(65, 65, 65))
    palette.setColor(palette.ToolTipBase, qcolor(90, 90, 90))
    palette.setColor(palette.ToolTipText, yellow)
    palette.setColor(palette.Text, yellow)
    palette.setColor(palette.Button, qcolor(40, 40, 40))
    palette.setColor(palette.ButtonText, yellow)
    palette.setColor(palette.BrightText, light_yellow)
    palette.setColor(palette.Link, light_yellow)
    palette.setColor(palette.LinkVisited, yellow)

    palette.setColor(palette.Disabled, palette.Text, dark_yellow)
    palette.setColor(palette.Disabled, palette.ButtonText, dark_yellow)

    app.setPalette(palette)
