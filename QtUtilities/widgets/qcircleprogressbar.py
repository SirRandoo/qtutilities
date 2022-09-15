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
import enum

from PySide6 import QtCore, QtGui, QtWidgets

__all__ = ['QCircleProgressBar']


class QCircleProgressBar(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super(QCircleProgressBar, self).__init__(parent=parent)

        self._padding: float = 5.0
        self._value: int = 0
        self._maximum: int = 100
        self._minimum: int = 0

        self._progress_color: QtGui.QColor = QtGui.QColor(33, 150, 243)
        self._base_plate_color: QtGui.QColor = self.palette().color(self.backgroundRole())
        self._progress_back_color: QtGui.QColor = self._progress_color.darker()
        self._text_color: QtGui.QColor = self._base_plate_color

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self._text_format: str = "{}%"

    @property
    def text_format(self) -> str:
        return self._text_format

    @text_format.setter
    def text_format(self, value: str):
        self._text_format = value

    @property
    def text_color(self) -> QtGui.QColor:
        return self._text_color

    @text_color.setter
    def text_color(self, value: QtGui.QColor):
        self._text_color = value

    @property
    def padding(self) -> float:
        return self._padding

    @padding.setter
    def padding(self, value: float):
        self._padding = value

    @property
    def progress_color(self) -> QtGui.QColor:
        return self._progress_color

    @progress_color.setter
    def progress_color(self, value: QtGui.QColor):
        self._progress_color = value

    @property
    def base_plate_color(self) -> QtGui.QColor:
        return self._base_plate_color

    @base_plate_color.setter
    def base_plate_color(self, value: QtGui.QColor):
        self._base_plate_color = value

    @property
    def progress_back_color(self) -> QtGui.QColor:
        return self._progress_back_color

    @progress_back_color.setter
    def progress_back_color(self, value: QtGui.QColor):
        self._progress_back_color = value

    @property
    def minimum(self) -> int:
        return self._minimum

    @minimum.setter
    def minimum(self, value: int):
        self._minimum = value

    @property
    def maximum(self) -> int:
        return self._maximum

    @maximum.setter
    def maximum(self, value: int):
        self._maximum = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int):
        self._value = max(self._minimum, min(self._value, self._maximum))

    def increment_value(self):
        self.value += 1

    def decrement_value(self):
        self.value -= 1

    def sizeHint(self):
        return QtCore.QSize(32, 32)

    def paintEvent(self, event: QtGui.QPaintEvent):
        rect = self.contentsRect()
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(self.progressColor()))

        if rect.width() < rect.height():
            rect.setHeight(rect.width())

        elif rect.height() < rect.width():
            rect.setWidth(rect.height())

        font = painter.font()
        base = QtGui.QPainterPath()
        front = QtGui.QPainterPath()
        back = QtGui.QPainterPath()
        fore = QtGui.QPainterPath()

        base.addEllipse(QtCore.QRectF(rect))
        painter.fillPath(base, self.basePlateColor())

        back.addEllipse(QtCore.QRectF(
            rect.x() + self.padding,
            rect.y() + self.padding,
            rect.width() - (self.padding * 2),
            rect.height() - (self.padding * 2)
        ))
        painter.fillPath(back, self.progressBackColor())

        if self.value > 0:
            fore.moveTo(rect.center())
            fore.arcTo(QtCore.QRectF(
                rect.x() + self.padding,
                rect.y() + self.padding,
                rect.width() - (self.padding * 2),
                rect.height() - (self.padding * 2)
            ), 91, -(360 * self.value / self.maximum))
            fore.closeSubpath()
            painter.fillPath(fore, self.progressColor())

        front.addEllipse(QtCore.QRectF(
            rect.x() + self.padding * 2,
            rect.y() + self.padding * 2,
            rect.width() - (self.padding * 4),
            rect.height() - (self.padding * 4)
        ))
        painter.fillPath(front, self.basePlateColor())

        # noinspection StrFormat
        text_percent = self._text_format.format(int(round((self.value / self.maximum) * 100, 0)))
        text_width = rect.width() - (self.padding * 15)
        text_height = rect.height() - (self.padding * 15)
        scale_factor = text_width / painter.fontMetrics().width(text_percent)
        font_size = font.pointSizeF() * scale_factor
        font = QtGui.QFont()
        font.setPointSizeF(font_size)
        font_metrics = QtGui.QFontMetricsF(font)

        while (font_metrics.width(text_percent) > text_width) or (font_metrics.height() > text_height):
            font_metrics = QtGui.QFontMetricsF(font)
            font.setPointSizeF(font.pointSizeF() - 1)

            if font.pointSizeF() < 1:
                break

        painter.setFont(font)
        painter.setPen(QtGui.QPen(self.text_color))

        text_rect = QtCore.QRectF(
            (rect.width() / 2) - painter.fontMetrics().width(text_percent) / 2,
            ((rect.height() / 2) - painter.fontMetrics().height() / 2) - text_height / 20,
            text_width,
            text_height
        )
        painter.drawText(text_rect, text_percent)
