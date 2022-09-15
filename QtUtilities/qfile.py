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
import typing

from PySide6 import QtCore

__all__ = ['QFile']


class QFile(QtCore.QObject):
    def __init__(self, file, mode = None):
        if mode is None:
            mode = QtCore.QFile.ReadOnly | QtCore.QFile.Text

        super().__init__()
        self._file = QtCore.QFile(file)
        self._mode = mode

        self._null_content = 'Content is null'
        self._unreadable = 'File not readable'
        self._not_open = 'File not open'
        self._not_writeable = 'File not writable'
        self._unsupported_format = 'File contents is in an unsupported format'

    def read_all(self) -> typing.AnyStr:
        if not self._file.isOpen():
            raise IOError(self._not_open)

        if not self._file.isReadable():
            raise IOError(self._unreadable)

        self._file.seek(0)
        content = self._file.readAll()

        if content.isNull():
            raise IOError(self._null_content)

        if self.is_binary():
            return content.data()

        elif self.is_text():
            return content.data().decode()

        else:
            raise IOError(self._unsupported_format)

    def read_line(self) -> typing.AnyStr:
        if not self._file.isOpen():
            raise IOError(self._not_open)

        if not self._file.isReadable():
            raise IOError(self._unreadable)

        content = self._file.readLine()

        if content.isNull():
            raise IOError(self._null_content)

        if self.is_binary():
            return content.data()

        elif self.is_text():
            return content.data().decode()

        else:
            raise IOError(self._unsupported_format)

    def read(self, size) -> typing.AnyStr:
        if not self._file.isOpen():
            raise IOError(self._not_open)

        if not self._file.isReadable():
            raise IOError(self._unreadable)

        content = self._file.read(size)

        if content.isNull():
            raise IOError(self._null_content)

        if self.is_binary():
            return content.data()

        elif self.is_text():
            return content.data().decode()

        else:
            raise IOError(self._unsupported_format)

    def write(self, content) -> int:
        if not self._file.isOpen():
            raise IOError(self._not_open)

        if not self._file.isWritable():
            raise IOError(self._not_writable)

        return self._file.write(content.encode() if isinstance(content, str) else content)

    def seek(self, position) -> bool:
        if not self._file.isOpen():
            raise IOError(self._not_open)

        return self._file.seek(position)

    def close(self):
        if not self._file.isOpen():
            raise IOError(self._not_open)

        self._file.close()

    def at_end(self) -> bool:
        if not self._file.isOpen():
            raise IOError(self._not_open)

        return self._file.atEnd()

    def size(self) -> int:
        if not self._file.isOpen():
            raise IOError(self._not_open)

        return self._file.size()

    def is_binary(self) -> bool:
        return not bool(self._mode & QtCore.QFile.Text)

    def is_text(self) -> bool:
        return bool(self._mode & QtCore.QFile.Text)

    def __enter__(self) -> 'QFile':
        if not self._file.isOpen():
            self._file.open(self._mode)

        if self._file.error() == QtCore.QFile.PermissionsError:
            raise PermissionError(self._file.errorString())

        elif self._file.error() == QtCore.QFile.UnspecifiedError:
            raise IOError(self._file.errorString())

        elif self._file.error() == QtCore.QFile.AbortError:
            raise IOError(self._file.errorString())

        elif self._file.error() == QtCore.QFile.OpenError:
            raise IOError(self._file.errorString())

        elif self._file.error() == QtCore.QFile.ResourceError:
            raise IOError(self._file.errorString())

        elif self._file.error() == QtCore.QFile.FatalError:
            raise RuntimeError(self._file.errorString())

        else:
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file.isOpen():
            self._file.flush()
            self._file.close()

        self.deleteLater()
