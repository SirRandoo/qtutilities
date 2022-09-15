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

__all__ = ['QGauge']


class QGauge(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super(QGauge, self).__init__(parent=parent)

        self._value: float = 0.0
        self._maximum: float = 100.0
        self._minimum: float = 0.0
        self._text: str = ''

        self._gauge_color: QtGui.QColor = QtGui.QColor(33, 150, 243)
        self._back_color: QtGui.QColor = self._gauge_color.darker()
        self._plate_color: QtGui.QColor = self.palette().color(self.backgroundRole())
        self._text_color: QtGui.QColor = self._plate_color

        self._padding: float = 3.0
        self._gauge_depth_angle: float = 270

    def paintEvent(self, event: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self)

        gauge_rect = self.contentsRect()
        base_p_back = QtGui.QPainterPath()
        base_p_fore = QtGui.QPainterPath()
        gauge_fore = QtGui.QPainterPath()
        gauge_back = QtGui.QPainterPath()

        base_p_back.moveTo(gauge_rect.center())
        base_p_back.arcTo(QtCore.QRectF(gauge_rect), 0, self._gauge_depth_angle)
        base_p_back.closeSubpath()
        painter.fillPath(base_p_back, self.base_plate_color())

        gauge_back.moveTo(QtCore.QPointF(gauge_rect.center().x(), gauge_rect.center().y() - self.padding))
        gauge_back.arcTo(QtCore.QRectF(
            gauge_rect.x() + self.padding,
            gauge_rect.y() + self.padding,
            gauge_rect.width() - self.padding * 2,
            gauge_rect.height() - self.padding * 4
        ), -270 - self._gauge_depth_angle / 2, self._gauge_depth_angle)
        gauge_back.closeSubpath()
        painter.fillPath(gauge_back, self.background_color)

        gauge_fore.moveTo(QtCore.QPointF(gauge_rect.center().x(), gauge_rect.center().y() - self.padding))
        gauge_fore.arcTo(QtCore.QRectF(
            gauge_rect.x() + self.padding,
            gauge_rect.y() + self.padding,
            gauge_rect.width() - self.padding * 2,
            gauge_rect.height() - self.padding * 4
        ), 360 - self._gauge_depth_angle / 2, -(self._gauge_depth_angle * self.value / self.maximum))
        gauge_fore.closeSubpath()
        painter.fillPath(gauge_fore, self.gauge_color)

        base_p_fore.moveTo(gauge_rect.center())
        base_p_fore.arcTo(QtCore.QRectF(
            gauge_rect.x() + self.padding * 8,
            gauge_rect.y() + self.padding * 8,
            gauge_rect.width() - self.padding * 16,
            gauge_rect.height() - self.padding * 16
        ), 0, 360)
        base_p_fore.closeSubpath()
        painter.fillPath(base_p_fore, self.base_plate_color())

        if len(self.text) <= 0:
            return

        gauge_font = painter.font()
        text_width = gauge_rect.width() - (self.padding * 50)
        text_height = gauge_rect.height() / 2 + (self.padding * 15)
        scale_factor = text_width / painter.fontMetrics().width(self.text)
        font_size = gauge_font.pointSizeF() * scale_factor
        font = QtGui.QFont()
        font.setPointSizeF(font_size)
        font_metrics = QtGui.QFontMetricsF(font)

        while (font_metrics.width(self.text) > text_width) or (font_metrics.height() > text_height):
            font_metrics = QtGui.QFontMetricsF(font)
            font.setPointSizeF(font.pointSizeF() - 1)

            if font.pointSizeF() < 1:
                break

        painter.setFont(font)
        painter.setPen(QtGui.QPen(self.text_color.darker()))

        text_rect = QtCore.QRectF(
            (gauge_rect.width() / 2) - painter.fontMetrics().width(self.text) / 2,
            (text_height / 2) - (painter.fontMetrics().height() / 2),
            text_width,
            text_height
        )
        painter.drawText(text_rect, self.text, QtGui.QTextOption())

    def sizeHint(self):
        return QtCore.QSize(20, 190)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value

    @property
    def padding(self) -> float:
        return self._padding

    @padding.setter
    def padding(self, value: float):
        self._padding = value

    @property
    def gauge_color(self) -> QtGui.QColor:
        return self._gauge_color

    @gauge_color.setter
    def gauge_color(self, value: QtGui.QColor):
        self._gauge_color = value

    @property
    def background_color(self) -> QtGui.QColor:
        return self._back_color

    @background_color.setter
    def background_color(self, value: QtGui.QColor):
        self._back_color = value

    @property
    def plate_color(self) -> QtGui.QColor:
        return self._plate_color

    @plate_color.setter
    def plate_color(self, value: QtGui.QColor):
        self._plate_color = value

    @property
    def text_color(self) -> QtGui.QColor:
        return self._text_color

    @text_color.setter
    def text_color(self, value: QtGui.QColor):
        self._text_color = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float):
        self._value = max(self._minimum, min(self._value, self._maximum))

    @property
    def minimum(self) -> float:
        return self._minimum

    @minimum.setter
    def minimum(self, value: float):
        self._minimum = value

        if self.value < value:
            self.value = value

    @property
    def maximum(self) -> float:
        return self._maximum

    @maximum.setter
    def maximum(self, value: float):
        self._maximum = value

        if self.value > value:
            self.value = value

    def increment_value(self):
        self.value += 1

    def decrement_value(self):
        self.value -= 1
