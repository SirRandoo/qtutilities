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
from typing import List, TYPE_CHECKING, Tuple, Union

from PySide6 import QtWidgets

if TYPE_CHECKING:
    HEADER: Union[str, QtWidgets.QTableWidgetItem]

__all__ = ['QTable']

from ..utils import append_table, safe_clear_table


class QTable(QtWidgets.QTableWidget):
    """A custom QTableWidget that adds convenience methods."""

    def horizontal_headers(self) -> List[QtWidgets.QTableWidgetItem]:
        """Returns the current horizontal headers in the QTableWidget."""
        return [self.horizontalHeaderItem(c) for c in range(self.columnCount())]

    def vertical_headers(self) -> List[QtWidgets.QTableWidgetItem]:
        """Returns the current vertical headers in the QTableWidget."""
        return [self.verticalHeaderItem(r) for r in range(self.rowCount())]

    def preserved_clear(self):
        """Clears the contents of the table while preserving the existing
        horizontal headers."""
        safe_clear_table(self)

    def set_horizontal_headers(self, *headers: HEADER):
        """Sets the horizontal headers for the QTableWidget."""
        self.setColumnCount(len(headers))

        for index, header in enumerate(headers):
            self.setHorizontalHeaderItem(
                index,
                header if isinstance(header, QtWidgets.QTableWidgetItem) else QtWidgets.QTableWidgetItem(header)
            )

    def set_vertical_headers(self, *headers: HEADER):
        """Sets the vertical headers for the QTableWidget."""
        for index, header in enumerate(headers):
            self.setVerticalHeaderItem(
                index,
                header if isinstance(header, QtWidgets.QTableWidgetItem) else QtWidgets.QTableWidgetItem(header)
            )

    def append(self, *args, **kwargs):
        """Appends the supplied data to the table.

        If data is passed through *args, it will be appended from
        left to right, or right to left depending on the current locale.

        If data is passed through **kwargs, the column in the new row will be
        set to the passed value.  If a header contains spaces, an underscore
        can be passed in place of it."""

        if args:
            self.setRowCount(self.rowCount() + 1)

            if len(args) > self.columnCount():
                raise IndexError

            for column, arg in enumerate(args):
                self.setItem(
                    self.rowCount() - 1,
                    column,
                    arg if isinstance(arg, QtWidgets.QTableWidgetItem) else QtWidgets.QTableWidgetItem(arg)
                )

        elif kwargs:
            append_table(self, **kwargs)

    def set_row(self, row: int, *args, **kwargs):
        """Modifies the specified row in the table.

        If data is passed through *args, the row will be modified from left to
        right, or right to left depending on the current locale.

        If data is passed through **kwargs, the column in `row` will be set to
        the passed value.  If a header contains spaces, an underscore can be
        passed in place of it."""

        if args:
            if len(args) > self.columnCount():
                raise IndexError

            for column, arg in enumerate(args):
                self.setItem(
                    row,
                    column,
                    arg if isinstance(arg, QtWidgets.QTableWidgetItem) else QtWidgets.QTableWidgetItem(arg)
                )

        elif kwargs:
            for column in [self.horizontalHeaderItem(column) for column in range(self.columnCount())
                           if self.horizontalHeaderItem(column).text().replace(' ', '_') in kwargs]:
                value = kwargs[column.text().replace(' ', '_')]

                self.setItem(
                    row,
                    column,
                    value if isinstance(value, QtWidgets.QTableWidgetItem) else QtWidgets.QTableWidgetItem(value)
                )

    def row_from_data(self, **data) -> int:
        """Returns the first row that matches the specified data."""
        for row in range(self.rowCount()):
            row_contents = {}

            for column in range(self.columnCount()):
                header, item = self.horizontalHeaderItem(column), self.item(row, column)
                row_contents[header.text().replace(' ', '_')] = item.text()

            if all([data[k] == row_contents[k] for k in data]):
                return row

        raise LookupError

    def row_from_header(self, header: str) -> Tuple[int, QtWidgets.QTableWidgetItem]:
        """Returns the first row that matches the specified vertical header."""
        for row in range(self.rowCount()):
            row_header: QtWidgets.QTableWidgetItem = self.verticalHeaderItem(row)

            if row_header.text().replace(' ', '_') == header:
                return row, row_header

        raise LookupError

    def set_row_header(self, row: int, header: HEADER):
        """Sets the vertical header for `row` to `header`."""
        if row > self.rowCount() or row < 0:
            raise IndexError

        self.setVerticalHeaderItem(
            row,
            header if isinstance(header, QtWidgets.QTableWidgetItem) else QtWidgets.QTableWidgetItem(header)
        )

    def set_column_header(self, column: int, header: HEADER):
        """Sets the horizontal header for `column` to `header`."""
        if column > self.columnCount() or column < 0:
            raise IndexError

        self.setHorizontalHeaderItem(
            column,
            header if isinstance(header, QtWidgets.QTableWidgetItem) else QtWidgets.QTableWidgetItem(header)
        )
