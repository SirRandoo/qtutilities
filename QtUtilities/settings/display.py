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
import inspect
from collections import namedtuple
from typing import Callable, Dict, NamedTuple, Optional, TYPE_CHECKING, Union

from PySide6 import QtCore, QtGui, QtWidgets

from . import converters
from .setting import Setting
from .view import View

__all__ = ['Display']


class Display(QtWidgets.QDialog):
    """A pre-built settings display."""

    def __init__(self, *, parent: QtWidgets.QWidget = None):
        # Super call
        super(Display, self).__init__(parent=parent)

        # Internal attributes
        self.tree: Optional[QtWidgets.QTreeWidget] = None
        self.stacked: Optional[QtWidgets.QStackedWidget] = None
        self.splitter: Optional[QtWidgets.QSplitter] = None
        self.container: Optional[QtWidgets.QWidget] = None

        self.view: Dict[str, View] = {}
        self.converters: Dict[str, Callable[[Setting], QtWidgets.QWidget]] = {
            name: instance
            for name, instance in inspect.getmembers(converters)
            if callable(instance)
        }

        self._setup: bool = False

        # Top-level settings.
        self.settings: Dict[str, Setting] = {}

    def register_setting(self, setting: Setting):
        """Registers a top-level setting to the display.  If the setting already
        exists, KeyError will be raised."""
        if setting.key in self.settings:
            raise KeyError(f'Setting {setting.key} is already registered!')

        self.settings[setting.key] = setting

    def unregister_setting(self, setting: Setting):
        """Unregisters a top-level setting from the display.  If the setting
        display doesn't exist, KeyError will be raised."""
        if setting.key not in self.settings:
            raise KeyError(f'Setting {setting.key} does not exist!')

        del self.settings[setting.key]

    def register_converter(self, converter: Callable[[Setting], QtWidgets.QWidget]):
        """Registers a converter to the settings display.  If the converter
        already exists, KeyError will be raised."""
        if converter.__name__ in self.converters:
            raise KeyError(f'Converter {converter.__name__} is already registered!')

        self.converters[converter.__name__] = converter

    def unregister_converter(self, converter: Union[str, Callable[[Setting], None]]):
        """Unregisters a converter from the settings display.  If the converter
        doesn't exist, KeyError will be raised."""
        n = converter.__name__ if callable(converter) else converter

        if n not in self.converters:
            raise KeyError(f'Converter {n} does not exist!')

        del self.converters[n]

    def setup_ui(self):
        """Checks up on the display to see if any objects need to be recreated."""
        if self.tree is None:
            self.tree = QtWidgets.QTreeWidget()
            self.tree.setHeaderHidden(True)
            self.tree.setEditTriggers(self.tree.NoEditTriggers)

            self.tree.setIndentation(14)
            self.tree.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
            self.tree.currentItemChanged.connect(self.tree_tracker)

        if self.stacked is None:
            self.stacked = QtWidgets.QStackedWidget()
            self.stacked.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        if self.container is None:
            self.container = QtWidgets.QWidget()

        if self.splitter is None:
            self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        layout: QtWidgets.QHBoxLayout = self.layout()

        if layout is None:
            layout = QtWidgets.QHBoxLayout(self)

        layout.addWidget(self.splitter)

        if self.splitter.indexOf(self.tree) == -1:
            self.splitter.insertWidget(0, self.tree)

        if self.splitter.indexOf(self.stacked) == -1:
            self.splitter.addWidget(self.stacked)

        for setting in self.settings.values():
            self._check_setting_ui(setting)

        for view in self.view:
            segments = view.split('/')
            s = self.settings

            for segment in segments:
                s = s[segment]

            self.view[view].item.setHidden(s.hidden)

        self.splitter.moveSplitter(80, 1)

    def _check_setting_ui(self, setting: Setting):
        """Creates a display for the settings object."""
        parent: Optional[QtCore.QObject] = setting.parent()
        path = setting.full_path

        if path not in self.view:
            self._create_view(path)

        view = self.view[path]

        if setting.converter is not None and setting.converter in self.converters:
            c = self.converters[setting.converter]
            view.display = c(setting)
            view.ensure_windows_hidden()

        else:
            c = self._get_converter_for(setting)

            if c is not None:
                view.display = c(setting)
                view.ensure_windows_hidden()

        for d in setting.descendants():
            self._check_setting_ui(d)

        if view.display is not None:
            view.display.setToolTip(setting.tooltip or None)
            view.display.setDisabled(setting.read_only)
            view.display.setWhatsThis(setting.whats_this)
            view.display.setStatusTip(setting.status_tip)

            view.item.setText(0, setting.display_name)
            view.item.setHidden(setting.hidden)

            if parent is not None and isinstance(parent, Setting):
                parent_view = self.view[parent.full_path]
                view.populate_display(setting, parent_view if isinstance(parent_view, Setting) else None)

                if any([not s.hidden for s in setting.descendants() if
                        isinstance(s, Setting)]) and parent_view.item.indexOfChild(view.item) == -1:
                    parent_view.item.addChild(view.item)

                if view.item.childCount() > 0:
                    view.item.setText(0, setting.key.replace('_', ' ').title())

                if setting.value is not None:
                    parent_layout: QtWidgets.QFormLayout = parent_view.container.layout()

                    if parent_layout is None:
                        parent_layout = QtWidgets.QFormLayout(parent_view.container)
                        parent_layout.setLabelAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

                    parent_layout.addRow(setting.display_name, view.display)

            else:
                self.tree.addTopLevelItem(view.item)

        else:
            if parent is not None and isinstance(parent, Setting):
                parent_view = self.view[parent.full_path]

                if any([not s.hidden for s in setting.descendants() if
                        isinstance(s, Setting)]) and parent_view.item.indexOfChild(view.item) == -1:
                    parent_view.item.addChild(view.item)

                if view.item.childCount() > 0:
                    view.item.setText(0, setting.key.replace('_', ' ').title())

            else:
                self.tree.addTopLevelItem(view.item)

            view.item.setHidden(setting.hidden)
            view.item.setDisabled(setting.read_only)
            view.item.setWhatsThis(0, setting.whats_this)
            view.item.setStatusTip(0, setting.status_tip)
            view.item.setToolTip(0, setting.tooltip or None)
            view.item.setText(0, setting.display_name)

    def _create_view(self, path: str):
        view = View.create(None, QtWidgets.QWidget(), QtWidgets.QTreeWidgetItem())
        view.ensure_windows_hidden()

        self.stacked.addWidget(view.container)
        self.view[path] = view

    @staticmethod
    def _get_converter_for(setting) -> Optional[Callable[[Setting], QtWidgets.QWidget]]:
        if isinstance(setting.value, bool):
            return converters.boolean
        elif isinstance(setting.value, float):
            return converters.decimal
        elif isinstance(setting.value, int):
            return converters.number
        elif isinstance(setting.value, str) and len(setting.value) <= 255:
            return converters.string
        elif isinstance(setting.value, str) and len(setting.value) > 255:
            return converters.long_string

    # Serialization
    def to_data(self) -> list:
        """Creates a list object from this display's setting data."""
        return [s.to_data() for s in self.settings.values()]

    @classmethod
    def from_data(cls, data: list) -> 'Display':
        """Creates a new Display object from raw data."""
        obj = cls()

        for setting in data:
            obj.register_setting(Setting.from_data(setting))

        return obj

    # Slots
    def tree_tracker(self, current: QtWidgets.QTreeWidgetItem):
        """Tracks changes in the QTreeWidget's selection box."""
        for path, view in self.view.items():
            if view.item == current and self.stacked.indexOf(view.container) != -1:
                self.stacked.setCurrentWidget(view.container)

    # Events
    def showEvent(self, a0: QtGui.QShowEvent):
        if not self._setup:
            self._setup = True
            self.setup_ui()

    # Magic methods
    def __getitem__(self, item: str) -> Setting:
        return self.settings.__getitem__(item)

    def __contains__(self, item: str) -> bool:
        try:
            return bool(self.settings[item])

        except KeyError:
            return False
