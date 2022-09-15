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
from PySide6 import QtGui, QtWidgets

__all__ = ['QAnimatedSplash']


class QAnimatedSplash(QtWidgets.QSplashScreen):
    def __init__(self, movie: QtGui.QMovie, *, parent: QtWidgets.QWidget = None):
        super(QAnimatedSplash, self).__init__(parent=parent)

        self._movie = movie

    @property
    def movie(self):
        return self._movie

    @movie.setter
    def movie(self, value: QtGui.QMovie):
        self._movie = value

    def update_frame(self):
        self.setPixmap(self._movie.currentPixmap())
        self.update()

    def showEvent(self, a0: QtGui.QShowEvent):
        if self._movie is None:
            raise ValueError("No movie set!")

        self._movie.updated.connect(self.update_frame)
        self._movie.start()
