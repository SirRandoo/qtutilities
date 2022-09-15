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

__all__ = ['QSlideButton']


class QSlideButton(QtWidgets.QAbstractButton):
    """Represents a slider button similar to Android/iOS buttons."""
    ButtonPadding = 4
    RoundedRadius = 12

    def __init__(self, parent: QtWidgets.QWidget = None):
        super(QSlideButton, self).__init__(parent=parent)
        self.setCheckable(True)

        self._button_background_color = QtGui.QColor(204, 204, 204)
        self._button_foreground_color = QtGui.QColor(33, 150, 243)
        self._button_color = QtGui.QColor(255, 255, 255)

        self._circular = True
        self._animation_scheduled = False
        self._button_x_offset = self.ButtonPadding

        self.toggled.connect(self.schedule_animation)

    @property
    def circular(self) -> bool:
        return self._circular

    @circular.setter
    def circular(self, value: bool):
        self._circular = value

    def schedule_animation(self):
        self._animation_scheduled = True

    def slide_button(self, painter: QtGui.QPainter):
        if self.width() <= 0 or self.height() <= 0:
            return

        path = QtGui.QPainterPath()
        path2 = QtGui.QPainterPath()

        width_distance = self.width() - self.height()
        button_x_offset_modifier = (width_distance / self.width()) / 10
        alpha_modifier = (1 / width_distance) * button_x_offset_modifier

        if self.isChecked():
            self._draw_checked(alpha_modifier, button_x_offset_modifier)

        else:
            self._draw_unchecked(alpha_modifier, button_x_offset_modifier)

        if self._button_x_offset >= (
                width_distance + self.ButtonPadding) or self._button_x_offset <= self.ButtonPadding:
            if self._button_x_offset > (width_distance + self.ButtonPadding):
                self._button_x_offset = width_distance + self.ButtonPadding

            elif self._button_x_offset < self.ButtonPadding:
                self._button_x_offset = self.ButtonPadding

            self._animation_scheduled = False

        else:
            if not self.circular:
                self._draw_square_nob(painter, width_distance)

            elif self.circular:
                self._draw_circular_nob(painter, path, path2)

    def _draw_circular_nob(self, painter, path, path2):
        path.addRoundedRect(QtCore.QRectF(self.rect()), self.RoundedRadius, self.height() // 2)
        painter.fillPath(path, self._button_background_color)
        painter.fillPath(path, self._button_foreground_color)
        path2.addEllipse(QtCore.QRectF(
            self._button_x_offset,
            self.ButtonPadding,
            self.height() - self.ButtonPadding * 2,
            self.height() - self.ButtonPadding * 2
        ))
        painter.fillPath(path2, self._button_color)
        painter.drawPath(path)

    def _draw_square_nob(self, painter, width_distance):
        self._draw_square_button(painter)
        painter.fillRect(QtCore.QRect(
            self._button_x_offset,
            self.ButtonPadding,
            width_distance - self.ButtonPadding * 2,
            self.height() - self.ButtonPadding * 2
        ), self._button_color)

    def _draw_unchecked(self, alpha_modifier, button_x_offset_modifier):
        new_alpha = self._button_foreground_color.alphaF() - alpha_modifier
        if new_alpha < 0:
            new_alpha = 0
        self._button_foreground_color.setAlphaF(new_alpha)
        self._button_x_offset -= button_x_offset_modifier

    def _draw_checked(self, alpha_modifier, button_x_offset_modifier):
        new_alpha = self._button_foreground_color.alphaF() + alpha_modifier
        if new_alpha > 1:
            new_alpha = 1
        self._button_foreground_color.setAlphaF(new_alpha)
        self._button_x_offset += button_x_offset_modifier

    def paintEvent(self, event: QtGui.QPaintEvent):
        if self.height() <= 0 or self.width() <= 0:
            return

        painter = QtGui.QPainter(self)
        path = QtGui.QPainterPath()
        path2 = QtGui.QPainterPath()
        pen = QtGui.QPen(QtCore.Qt.NoPen)

        painter.setPen(pen)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        width_distance = self.width() - self.height()

        if not self._animation_scheduled:
            self._modify_button_alpha()
            self._draw_button(painter, path)

            if not self.circular:
                painter.fillRect(self._get_switch_rect(width_distance), self._button_color)

            elif self.circular:
                path2.addEllipse(QtCore.QRectF(
                    self._button_x_offset,
                    self.ButtonPadding,
                    self.height() - self.ButtonPadding * 2,
                    self.height() - self.ButtonPadding * 2
                ))

                painter.fillPath(path2, self._button_color)
                painter.drawPath(path2)

        else:
            if self._button_x_offset >= (width_distance + self.ButtonPadding) \
                    or self._button_x_offset <= self.ButtonPadding:
                self._button_foreground_color.setAlpha(0 if self.isChecked() else 255)

            self.slide_button(painter)
            self.update()

    def _get_switch_rect(self, width_distance):
        if self.isChecked():
            switch_rect = QtCore.QRect(
                width_distance + self.ButtonPadding,  # X Position
                self.ButtonPadding,  # Y Position
                width_distance - self.ButtonPadding * 2,  # Width
                self.height() - self.ButtonPadding * 2  # Height
            )

        else:
            switch_rect = QtCore.QRect(
                self.ButtonPadding,  # X Position
                self.ButtonPadding,  # Y Position
                width_distance - self.ButtonPadding * 2,  # Width
                self.height() - self.ButtonPadding * 2  # Height
            )
        return switch_rect

    def _draw_button(self, painter, path):
        if not self.circular:
            self._draw_square_button(painter)

        else:
            self._draw_circular_button(painter, path)

    def _draw_circular_button(self, painter, path):
        path.addRoundedRect(QtCore.QRectF(self.rect()), self.RoundedRadius, self.height())
        painter.fillPath(path, self._button_background_color)
        painter.fillPath(path, self._button_foreground_color)

    def _draw_square_button(self, painter):
        painter.fillRect(self.rect(), self._button_background_color)
        painter.fillRect(self.rect(), self._button_foreground_color)

    def _modify_button_alpha(self):
        if self.isChecked():
            self._maximize_button_alpha()

        else:
            self._minimize_button_alpha()

    def _minimize_button_alpha(self):
        if self._button_foreground_color.alpha() > 0:
            self._button_foreground_color.setAlpha(0)

    def _maximize_button_alpha(self):
        if self._button_foreground_color.alpha() < 255:
            self._button_foreground_color.setAlpha(255)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        if (self._button_x_offset > self.ButtonPadding) and not self._animation_scheduled:
            self._button_x_offset = (self.width() - self.height()) + self.ButtonPadding

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(32, 23)
