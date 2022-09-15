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
import logging
import typing

import PySide6
from PySide6 import QtCore, QtWidgets

__all__ = ['append_table', 'clear_table', 'populate_table', 'safe_clear_table',
           'set_table_headers', 'qt_message_handler']


def clear_table(table: QtWidgets.QTableWidget, headers: typing.List[str] = None):
    """Clears ALL data from the passed table, including headers.

    :param table: The QTableWidget to clear.
    :param headers: A list of strings representing the new headers to fill the
                    table with. This should be in order from left to right."""
    table.clear()
    set_table_headers(table, ['Key', 'Value'] if not headers else headers)


def safe_clear_table(table: QtWidgets.QTableWidget, headers: typing.List[str] = None):
    """Clears the contents from the passed table while preserving its current
    headers.

    :param table: The QTableWidget to clear.
    :param headers: A list of strings representing the new headers to fill the
                    table with. This should be in order from left to right."""

    if headers is None:
        headers = []

    _current_headers = [table.horizontalHeaderItem(column).text() for column in range(table.columnCount())]

    for header in headers:
        if header not in _current_headers:
            _current_headers.append(header)

    table.clear()
    table.setRowCount(0)

    for index, header in enumerate(_current_headers):
        table.setHorizontalHeaderItem(index, QtWidgets.QTableWidgetItem(str(header)))


def set_table_headers(table: QtWidgets.QTableWidget, headers: typing.List[str]):
    """Sets the passed table's horizontal headers to the strings provided.

    :param table: The QTableWidget to set the table headers for.
    :param headers: A list of strings representing the headers to populate the
                    table with. The collection passed will be read from left to
                    right."""
    for index, header in enumerate(headers):
        table.setHorizontalHeaderItem(index, QtWidgets.QTableWidgetItem(str(header)))


def append_table(table: QtWidgets.QTableWidget, **data: str):
    """Appends the supplied data to the table.

    :param table: The QTableWidget to append the data to.
    :param data: A dictionary object representing the data to append to the
                 table. The dictionary keys should be the headers to append the
                 values to."""
    table.setRowCount(table.rowCount() + 1)

    for column_index in range(table.columnCount()):
        _column_header = table.horizontalHeaderItem(column_index).text()

        if _column_header not in data:
            continue

        table.setItem(table.rowCount() - 1, column_index, QtWidgets.QTableWidgetItem(data[_column_header]))


def populate_table(table: QtWidgets.QTableWidget, data: typing.List[typing.Dict[str, str]]):
    """Populates a QTableWidget with the data provided

    :param table: The QTableWidget to populate with the data provided.
    :param data: A collection of data to populate into the specified table. The
                 collection represents rows, whereas the collection's contents
                 represent the content for those rows. The contents should be
                 passed as a dictionary where the keys correspond to the table's
                 headers, and the values for those keys correspond to the cells
                 to populate with the values."""
    safe_clear_table(table)

    for record in data:
        append_table(table, **record)


def qt_message_handler(message_type: QtCore.QtMsgType, context: QtCore.QMessageLogContext, message: str):
    """A custom message handler for wrapping Qt's log messages with Python's
    logging module."""
    logger = logging.getLogger(f'Qt{PySide6.__version_info__[0]}')
    function = getattr(context, 'function', 'INTERNAL')
    line_number = getattr(context, 'line', -1)
    level = logging.NOTSET

    if message_type == QtCore.QtMsgType.QtDebugMsg:
        level = logging.DEBUG
    elif message_type == QtCore.QtMsgType.QtCriticalMsg:
        level = logging.CRITICAL
    elif message_type == QtCore.QtMsgType.QtWarningMsg:
        level = logging.WARNING
    elif message_type == QtCore.QtMsgType.QtInfoMsg or message_type == QtCore.QtMsgType.QtSystemMsg:
        level = logging.INFO
    elif message_type == QtCore.QtMsgType.QtFatalMsg:
        level = logging.FATAL

    logger.handle(logger.makeRecord(logger.name, level, function, line_number, message, {}, None))
