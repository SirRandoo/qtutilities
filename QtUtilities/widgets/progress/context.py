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
from typing import Union

from PySide6 import QtCore, QtWidgets

from QtUtilities import signals

__all__ = ['Context']


class Context(QtWidgets.QDialog):
    """A special progress dialog that works as a context manager."""

    def __init__(self, maximum: int = None, reverse: bool = None):
        super(Context, self).__init__(flags=QtCore.Qt.WindowSystemMenuHint)

        self._progress = QtWidgets.QProgressBar(parent=self)
        self._label = QtWidgets.QLabel("Loading...", parent=self)
        self._layout = QtWidgets.QVBoxLayout(self)
        self._reversed = bool(reverse)

        self._layout.addWidget(self._label)
        self._layout.addWidget(self._progress)

        self._progress.setRange(0, maximum if maximum is not None else 0)
        self._label.setAlignment(QtCore.Qt.AlignCenter)
        self._label.setWordWrap(True)
        self.setModal(True)

        if maximum is not None:
            self._progress.set_value(maximum if self._reversed else 0)

    def increment(self):
        """Increments the progress' value."""
        if not self._reversed:
            if self._progress.value() < self._progress.maximum():
                self._progress.set_value(self._progress.value() + 1)

        else:
            if self._progress.value() > self._progress.minimum():
                self._progress.set_value(self._progress.value() - 1)

    def decrement(self):
        """Decrements the progress' value."""
        if not self._reversed:
            if self._progress.value() > self._progress.minimum():
                self._progress.set_value(self._progress.value() - 1)

        else:
            if self._progress.value() < self._progress.maximum():
                self._progress.set_value(self._progress.value() + 1)

    def set_text(self, text: str):
        """Sets the label's text to `text`."""
        self._label.set_text(text)
        self.adjustSize()

    def threaded_task(self, label: str, func: callable, *args, **kwargs):
        """Executes a callable in a thread, while updating the dialog.

        :param label: The text to display when this task is executing
        :param func: The callable to execute"""
        self.set_text(label)

        thread = QtCore.QThread()
        thread.run = functools.partial(func, *args, **kwargs)

        thread.start()
        signals.wait_for_signal(thread.finished)

        self.increment()

    def task(self, label: str, func: callable, *args, **kwargs):
        """Executes a callable while updating the dialog.

        :param label: The text to display when this task is executing
        :param func: The callable to execute"""
        self.set_text(label)
        func(*args, **kwargs)
        self.increment()

    def wait_for_task(self, label: str, signal: Union[QtCore.Signal], *,
                      timeout: int = None, before: callable = None, threaded: bool = None):
        """Waits for a signal to be emitted before normal execution will proceed.

        :param label: The text to display when this task is executing
        :param signal: The signal to wait for
        :param timeout: The amount of seconds to wait before forcibly ending
        :param before: The callable to execute before waiting
        :param threaded: Whether or not the callable will be executed in a thread"""
        loop = QtCore.QEventLoop()
        self.set_text(label)

        signal.connect(loop.quit)

        if before is not None:
            if threaded:
                thread = QtCore.QThread()
                thread.run = before

                QtCore.QTimer.singleShot(1, thread.start)

            else:
                QtCore.QTimer.singleShot(1, before)

        if timeout:
            QtCore.QTimer.singleShot(timeout * 1000, loop.quit)

        loop.exec()

    @staticmethod
    def wait_for(signal, *, timeout: int = None, initiator: callable = None):
        """Waits for a signal to be emitted before continuing.  `timeout` is
        the amount of seconds to wait for.  `initiator` is the callable that
        will eventually emit `signal`."""
        loop = QtCore.QEventLoop()
        signal.connect(loop.quit)

        if timeout:
            QtCore.QTimer.singleShot(timeout * 1000, loop.quit)

        if initiator:
            QtCore.QTimer.singleShot(1, initiator)

        loop.exec()

    @staticmethod
    def delay(milliseconds: int = None):
        """A sleep-like method for the progress dialog."""
        if milliseconds is None:
            milliseconds = 1000  # 1 second

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(milliseconds, loop.quit)
        loop.exec()

    def __enter__(self):
        self.show()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done(0)
        self.deleteLater()
