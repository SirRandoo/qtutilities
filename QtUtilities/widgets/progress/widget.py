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
from PySide6 import QtCore, QtWidgets

__all__ = ['ProgressWidget']


class ProgressWidget(QtWidgets.QWidget):
    """Represents a label-progressbar pair within a widget."""

    def __init__(self, display_text: str = None, *, parent: QtWidgets.QWidget = None):
        super(ProgressWidget, self).__init__(parent=parent)

        self._label = QtWidgets.QLabel(parent=self)
        self._bar = QtWidgets.QProgressBar(parent=self)
        self._layout = QtWidgets.QVBoxLayout(self)

        self._layout.addWidget(self._label, 0, QtCore.Qt.AlignCenter)
        self._layout.addWidget(self._bar, 0, QtCore.Qt.AlignCenter)

        if display_text is not None:
            self.text = display_text

    @property
    def value(self) -> int:
        return self._bar.value()

    @value.setter
    def value(self, v: int):
        self._bar.setValue(v)

    @property
    def maximum(self) -> int:
        return self._bar.maximum()

    @maximum.setter
    def maximum(self, value: int):
        self._bar.setMaximum(value)

    @property
    def minimum(self) -> int:
        return self._bar.minimum()

    @minimum.setter
    def minimum(self, value: int):
        self._bar.setMinimum(value)

    @property
    def text(self) -> str:
        return self._label.text()

    @text.setter
    def text(self, value: str):
        self._label.setText(value)

    def set_range(self, minimum: int, maximum: int):
        self._bar.setRange(minimum, maximum)

    def increment(self):
        """Increments the progress bar's progress by 1."""
        self.value = min(self.value + 1, self.maximum)

    def decrement(self):
        """Decrements the progress bar's progress by 1."""
        self.value = max(self.value - 1, self.minimum)

    def reset(self):
        """Resets the progress widget's values."""
        self._label.clear()
        self._bar.reset()
