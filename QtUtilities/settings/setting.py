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

from PySide6 import QtCore

__all__ = ['Setting']


@dataclasses.dataclass()
class Setting(QtCore.QObject):
    """A unified settings object."""
    value_changed: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object)

    key: str
    value: typing.Any = dataclasses.field(default=None)

    tooltip: str = dataclasses.field(default=None)
    hidden: bool = dataclasses.field(default=False)
    converter: str = dataclasses.field(default=None)
    status_tip: str = dataclasses.field(default=None)
    whats_this: str = dataclasses.field(default=None)
    read_only: bool = dataclasses.field(default=False)
    display_name: str = dataclasses.field(default=None)
    data: dict = dataclasses.field(default_factory=dict)

    p: dataclasses.InitVar[QtCore.QObject] = dataclasses.field(default=None)

    def __post_init__(self, p: typing.Optional[QtCore.QObject]):
        super(Setting, self).__init__(parent=p)

        if self.display_name is None:
            self.display_name = self.key.replace('_', ' ').title()

        if self.tooltip is None:
            self.tooltip = ''

        if self.converter is None:
            if isinstance(self.value, bool):
                self.converter = 'boolean'

            elif isinstance(self.value, float):
                self.converter = 'decimal'

            elif isinstance(self.value, int):
                self.converter = 'number'

            elif isinstance(self.value, str) and len(self.value) <= 255:
                self.converter = 'char'

            elif isinstance(self.value, str) and len(self.value) > 255:
                self.converter = 'text'

    # Properties
    @property
    def full_path(self) -> str:
        """Returns the full path for this setting."""
        if self.parent():
            return '{}/{}'.format(self.parent().full_path, self.key)

        else:
            return self.key

    # Relationship methods
    def set_parent(self, parent: 'Setting'):
        """Sets the parent for this settings object."""
        if isinstance(parent, Setting):
            self.setParent(parent)

        else:
            raise TypeError('Parent must be of instance of Setting!')

    def add_child(self, child: 'Setting'):
        """Adds a child for this settings object."""
        if isinstance(child, Setting):
            child.set_parent(self)

        else:
            raise TypeError('Child must be of instance Setting!')

    def add_children(self, *children: 'Setting'):
        """Bulk adds children to this settings object."""
        for child in children:
            if isinstance(child, Setting):
                child.setParent(self)

            else:
                raise TypeError('Child must be of instance Setting!')

    @staticmethod
    def remove_child(child: 'Setting', *, new_parent: 'Setting' = None):
        """Removes a child from this settings object.

        If `new_parent` is not specified, the child will remain orphaned."""
        if isinstance(child, Setting):
            if new_parent is not None:
                child.set_parent(new_parent)

            else:
                # noinspection PyTypeChecker
                child.setParent(None)

        else:
            raise TypeError('Child must of instance Setting!')

    @staticmethod
    def remove_children(*children, new_parent: 'Setting' = None):
        """Bulk removes children from this settings object.

        If `new_parent` is not specified, the child will remain orphaned."""
        for child in children:
            if isinstance(child, Setting):
                if new_parent is not None:
                    child.set_parent(new_parent)

                else:
                    # noinspection PyTypeChecker
                    child.setParent(None)

            else:
                raise TypeError('Child must be of instance Setting!')

    def descendants(self) -> typing.List['Setting']:
        """Returns a list this setting's descendants."""
        return [c for c in self.children() if isinstance(c, Setting)]

    def set_value(self, value: typing.Any):
        """Sets the value of this setting."""
        self.value = value
        self.value_changed.emit(value)

    # Serialization methods
    @classmethod
    def from_data(cls, data: dict) -> 'Setting':
        """Creates a new Setting object from raw data."""
        inst: Setting = cls(key=data['key'], value=data.get('value'))

        inst.tooltip = data['tooltip']
        inst.hidden = data['hidden']
        inst.converter = data['converter']
        inst.status_tip = data['status_tip']
        inst.whats_this = data['whats_this']
        inst.read_only = data['read_only']
        inst.display_name = data['display_name']
        inst.data = data['data']

        for child in data.get('descendants'):  # type: dict
            c = Setting.from_data(child)
            inst.add_child(c)

        return inst

    def to_data(self) -> dict:
        """Creates a dict object from this setting's data."""
        return {
            'key': self.key,
            'value': self.value,
            'descendants': [d.to_data() for d in self.descendants()],
            'data': self.data,
            'read_only': self.read_only,
            'hidden': self.hidden,
            'tooltip': self.tooltip,
            'status_tip': self.status_tip,
            'whats_this': self.whats_this,
            'display_name': self.display_name,
            'converter': self.converter
        }

    # Magic methods
    def __repr__(self) -> str:
        return '<{0.__class__.__name__} key="{0.full_path}" children={1}>'.format(self, len(self.descendants()))

    def __getitem__(self, key: str) -> 'Setting':
        children = self.descendants()

        for child in children:
            if child.key == key:
                return child

        raise KeyError

    def __contains__(self, item: str) -> bool:
        try:
            return bool(self[item])

        except KeyError:
            return False
