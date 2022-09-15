"""
This file is part of QtUtilities.

QtUtilities is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

QtUtilities is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with QtUtilities.  If not, see <https://www.gnu.org/licenses/>.
"""
import dataclasses
import typing

from PySide6 import QtWidgets


if typing.TYPE_CHECKING:
    from .setting import Setting


__all__ = ['View']


@dataclasses.dataclass()
class View:
    display: typing.Optional[QtWidgets.QWidget]
    container: QtWidgets.QWidget
    item: QtWidgets.QTreeWidgetItem

    @classmethod
    def create(cls, display: typing.Optional[QtWidgets.QWidget], container: QtWidgets.QWidget,
               item: QtWidgets.QTreeWidgetItem) -> 'View':
        item.setFirstColumnSpanned(True)

        return View(display, container, item)

    def ensure_windows_hidden(self):
        if self.container.isWindow() and not self.container.isHidden():
            self.container.hide()

        if self.display is not None and self.display.isWindow() and not self.display.isHidden():
            self.display.hide()

    def populate_display(self, setting: 'Setting', parent: 'View' = None):
        if parent is not None:
            self.display.setParent(parent.container)

        self.display.setToolTip(setting.tooltip or None)
        self.display.setDisabled(setting.read_only)
        self.display.setWhatsThis(setting.whats_this)
        self.display.setStatusTip(setting.status_tip)

        self.item.setText(0, setting.display_name)
        self.item.setHidden(setting.hidden)
