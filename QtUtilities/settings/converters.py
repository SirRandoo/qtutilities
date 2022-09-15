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
import functools
import os

from PySide6 import QtCore, QtGui, QtWidgets

from .setting import Setting

__all__ = ['combo_box', 'modifiable_collection', 'directory', 'file', 'collection', 'string',
           'long_string', 'number', 'decimal', 'boolean']


def combo_box(obj: Setting) -> QtWidgets.QComboBox:
    """Converts a settings object into a visible QComboBox."""
    combobox = QtWidgets.QComboBox()

    if combobox.isWindow():
        combobox.hide()

    combobox.setMaxVisibleItems(obj.data.get('max_visible', 200))
    combobox.setMinimumContentsLength(obj.data.get('min_content_length', 1))

    if 'choices' in obj.data:
        for choice in obj.data.get('choices', []):
            if isinstance(choice, dict):
                if 'icon' in choice:
                    combobox.addItem(QtGui.QIcon(choice['icon']), choice.get('text', ''))
                else:
                    combobox.addItem(choice.get('text', ''))

            elif isinstance(choice, str):
                combobox.addItem(choice)

        combobox.setCurrentIndex(obj.value)

    obj.converter = 'combo_box'
    combobox.currentIndexChanged.connect(obj.set_value)

    return combobox


def font_box(obj: Setting) -> QtWidgets.QFontComboBox:
    """Converts a settings object into a visible QFontComboBox."""
    combobox = QtWidgets.QFontComboBox()

    if combobox.isWindow():
        combobox.hide()

    combobox.setMaxVisibleItems(obj.data.get('max_visible', 200))
    combobox.setMinimumContentsLength(obj.data.get('min_content_length', 1))
    combobox.setCurrentFont(QtGui.QFont(obj.value))
    obj.converter = 'font_box'

    def store_font(font: QtGui.QFont):
        obj.set_value(font.rawName())

    combobox.currentFontChanged.connect(store_font)

    return combobox


def file(obj: Setting) -> QtWidgets.QWidget:
    """Converts a settings object into a visible QWidget."""
    widget = QtWidgets.QWidget()
    line = QtWidgets.QLineEdit(parent=widget)
    button = QtWidgets.QToolButton(parent=widget)
    layout = QtWidgets.QHBoxLayout(widget)

    if widget.isWindow():
        widget.hide()

    def show_dialog():
        dialog = QtWidgets.QFileDialog()
        url, _ = dialog.getOpenFileUrl(parent=widget,
                                       caption='Select a file...',
                                       directory=os.getcwd())

        if url.isValid():
            path = url.toDisplayString(url.RemoveScheme | url.NormalizePathSegments).lstrip("/")
            line.setText(path)
            obj.set_value(path)

        dialog.deleteLater()

    layout.setContentsMargins(0, 0, 0, 0)
    button.setText('📂')
    layout.addWidget(line)
    layout.addWidget(button)

    if obj.value is not None:
        line.setText(str(obj.value))

    obj.converter = 'file'
    button.clicked.connect(show_dialog)

    return widget


def directory(obj: Setting) -> QtWidgets.QWidget:
    """Converts a settings object into a visible QWidget."""
    widget = QtWidgets.QWidget()
    line = QtWidgets.QLineEdit(parent=widget)
    button = QtWidgets.QToolButton(parent=widget)
    layout = QtWidgets.QHBoxLayout(widget)

    if widget.isWindow():
        widget.hide()

    def show_dialog():
        dialog = QtWidgets.QFileDialog()
        url: QtCore.QUrl = dialog.getExistingDirectoryUrl(parent=widget,
                                                          caption='Select a directory...',
                                                          directory=QtCore.QUrl(os.getcwd()))

        if url.isValid():
            path: str = url.toDisplayString(url.RemoveScheme | url.NormalizePathSegments).lstrip("/")
            line.setText(path)
            obj.set_value(path)

        dialog.deleteLater()

    layout.setContentsMargins(0, 0, 0, 0)
    button.setText('📂')
    layout.addWidget(line)
    layout.addWidget(button)

    if obj.value is not None:
        line.setText(str(obj.value))

    obj.converter = 'directory'
    button.clicked.connect(show_dialog)

    return widget


def collection(obj: Setting) -> QtWidgets.QWidget:
    """Converts a settings object into a QWidget."""
    # Declarations
    widget = QtWidgets.QWidget()
    surrogate = QtWidgets.QWidget(parent=widget)
    list_widget = QtWidgets.QListWidget(parent=widget)
    up = QtWidgets.QToolButton(parent=surrogate)
    down = QtWidgets.QToolButton(parent=surrogate)
    layout = QtWidgets.QHBoxLayout(widget)
    s_layout = QtWidgets.QVBoxLayout(surrogate)

    if widget.isWindow():
        widget.hide()

    def move_up():
        index = list_widget.currentRow()

        if index > 0:
            item = list_widget.takeItem(index)
            list_widget.insertItem(index - 1, item)
            list_widget.setCurrentRow(index - 1)

    def move_down():
        index = list_widget.currentRow()

        if index > 0 and list_widget.count() > 1:
            item = list_widget.takeItem(index)
            list_widget.insertItem(index + 1, item)
            list_widget.setCurrentRow(index + 1)

    up.setText('▲')
    down.setText('▼')
    layout.setContentsMargins(0, 0, 0, 0)
    s_layout.setContentsMargins(0, 0, 0, 0)
    list_widget.setEditTriggers(list_widget.DoubleClicked)
    list_widget.setViewMode(obj.data.get('view_mode', list_widget.ListMode))

    if not isinstance(obj.value, list):
        obj.set_value([obj.value])

    list_widget.addItems(obj.value)
    s_layout.addWidget(up)
    s_layout.addWidget(down)
    layout.addWidget(list_widget)
    layout.addWidget(surrogate)
    obj.converter = 'collection'
    up.clicked.connect(move_up)
    down.clicked.connect(move_down)

    return widget


def modifiable_collection(obj: Setting) -> QtWidgets.QWidget:
    """Converts a setting object into a QWidget."""
    widget = QtWidgets.QWidget()
    surrogate = QtWidgets.QWidget(parent=widget)
    list_widget = QtWidgets.QListWidget(parent=widget)
    add = QtWidgets.QToolButton(parent=surrogate)
    remove = QtWidgets.QToolButton(parent=surrogate)
    up = QtWidgets.QToolButton(parent=surrogate)
    down = QtWidgets.QToolButton(parent=surrogate)
    layout = QtWidgets.QHBoxLayout(widget)
    s_layout = QtWidgets.QVBoxLayout(surrogate)

    if widget.isWindow():
        widget.hide()

    def add_item():
        item = QtWidgets.QListWidgetItem()
        list_widget.addItem(item)
        list_widget.editItem(item)

    def remove_item():
        index = list_widget.currentRow()

        if index != -1:
            list_widget.takeItem(index)

    def move_up():
        index = list_widget.currentRow()

        if index > 0:
            item = list_widget.takeItem(index)
            list_widget.insertItem(index - 1, item)
            list_widget.setCurrentRow(index - 1)

    def move_down():
        index = list_widget.currentRow()

        if index > 0 and list_widget.count() > 1:
            item = list_widget.takeItem(index)
            list_widget.insertItem(index + 1, item)
            list_widget.setCurrentRow(index + 1)

    def save():
        data = []

        for index in range(list_widget.count()):
            item: QtWidgets.QListWidgetItem = list_widget.item(index)

            if item:
                data.append(item.text())

        obj.value = data

    add.setText('+')
    remove.setText('-')
    up.setText('▲')
    down.setText('▼')
    layout.setContentsMargins(0, 0, 0, 0)
    s_layout.setContentsMargins(0, 0, 0, 0)
    list_widget.setEditTriggers(list_widget.DoubleClicked)
    list_widget.setViewMode(obj.data.get('view_mode', list_widget.ListMode))

    if not isinstance(obj.value, list):
        obj.set_value([str(obj.value)])

    list_widget.addItems(obj.value)
    s_layout.addWidget(add)
    s_layout.addWidget(remove)
    s_layout.addWidget(up)
    s_layout.addWidget(down)
    layout.addWidget(list_widget)
    layout.addWidget(surrogate)
    obj.converter = 'modifiable_collection'
    add.clicked.connect(add_item)
    remove.clicked.connect(remove_item)
    up.clicked.connect(move_up)
    down.clicked.connect(move_down)

    list_widget.model().rowsInserted.connect(save)
    list_widget.model().rowsRemoved.connect(save)
    list_widget.model().rowsMoved.connect(save)

    return widget


def string(obj: Setting) -> QtWidgets.QLineEdit:
    """Converts a settings object into a QLineEdit."""
    line = QtWidgets.QLineEdit()

    if line.isWindow():
        line.hide()

    if obj.value is not None:
        line.setText(str(obj.value))

    line.setMaxLength(obj.data.get('max_length', 260))
    line.setClearButtonEnabled(obj.data.get('clear_button', False))
    line.setEchoMode(obj.data.get('echo_mode', line.Normal))
    line.setPlaceholderText(obj.data.get('placeholder', ''))
    obj.converter = 'string'
    line.textChanged.connect(obj.set_value)

    return line


def long_string(obj: Setting) -> QtWidgets.QTextEdit:
    """Converts a settings object into a QTextEdit."""
    edit = QtWidgets.QTextEdit()

    if edit.isWindow():
        edit.hide()

    if obj.value is not None:
        edit.setText(str(obj.value))

    obj.converter = 'long_string'
    edit.textChanged.connect(functools.partial(obj.set_value, edit.toPlainText()))

    # Return
    return edit


def number(obj: Setting) -> QtWidgets.QSpinBox:
    """Converts a settings object into a QSpinBox."""
    spin = QtWidgets.QSpinBox()

    if spin.isWindow():
        spin.hide()

    spin.setRange(obj.data.get('minimum', -1000000), obj.data.get('maximum', 1000000))
    spin.setButtonSymbols(obj.data.get('buttons', spin.UpDownArrows))
    spin.setGroupSeparatorShown(obj.data.get('separator', False))

    if obj.value is not None:
        spin.setValue(int(obj.value))

    obj.converter = 'number'
    spin.valueChanged.connect(obj.set_value)

    return spin


def decimal(obj: Setting) -> QtWidgets.QDoubleSpinBox:
    """Converts a settings object into a QDoubleSpinBox."""
    spin = QtWidgets.QDoubleSpinBox()

    if spin.isWindow():
        spin.hide()

    spin.setRange(obj.data.get('minimum', -1000000), obj.data.get('maximum', 1000000))
    spin.setGroupSeparatorShown(obj.data.get('separator', False))
    spin.setButtonSymbols(obj.data.get('buttons', spin.UpDownArrows))

    if obj.value is not None:
        spin.setValue(float(obj.value))

    obj.converter = 'decimal'
    spin.valueChanged.connect(obj.set_value)

    return spin


def boolean(obj: Setting) -> QtWidgets.QCheckBox:
    """Converts a settings object into a QCheckBox."""
    check = QtWidgets.QCheckBox()

    if check.isWindow():
        check.hide()

    def change_value(state: int):
        obj.set_value(state == QtCore.Qt.PartiallyChecked or state == QtCore.Qt.Checked)

    check.setTristate(obj.data.get('tristate', False))

    if obj.value is not None:
        check.setChecked(bool(obj.value))

    obj.converter = 'boolean'
    check.stateChanged.connect(change_value)

    return check
