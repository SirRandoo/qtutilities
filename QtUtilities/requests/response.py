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
import dataclasses
import functools
import io
import json
import typing

from PySide6 import QtCore, QtNetwork

from .. import signals

__all__ = ['Response']


@dataclasses.dataclass(frozen=True)
class Response:
    """The response from a factory request.  This alone does nothing without a
    QNetworkReply to populate itself."""
    urls: typing.List[QtCore.QUrl] = dataclasses.field(init=False, default_factory=list)
    params: typing.Dict[str, str] = dataclasses.field(init=False, default_factory=dict)
    host: str = dataclasses.field(init=False, default_factory=str)
    scheme: str = dataclasses.field(init=False, default_factory=str)
    domain: str = dataclasses.field(init=False, default_factory=str)
    port: int = dataclasses.field(init=False, default_factory=int)
    cookies: typing.Dict[str, typing.Any] = dataclasses.field(init=False, default_factory=dict)
    all_headers: typing.List[typing.Dict[str, str]] = dataclasses.field(init=False, default_factory=list)
    code: int = dataclasses.field(init=False, default=QtNetwork.QNetworkReply.NoError)
    error_string: str = dataclasses.field(init=False, default_factory=str)
    raw_content: io.BytesIO = dataclasses.field(init=False, default_factory=io.BytesIO)

    # Properties
    @property
    def url(self) -> QtCore.QUrl:
        """The last QUrl the request was redirected through, assuming redirects
        are allowed.  If no urls were cached, an empty QUrl will be returned."""
        try:
            return self.urls[-1]

        except IndexError:
            return QtCore.QUrl()

    @property
    def headers(self) -> typing.Dict[str, typing.Union[str, int, float]]:
        """The last headers the request obtained from the host.  If no headers
        were received, an empty dict will be returned."""
        try:
            return self.all_headers[-1]

        except IndexError:
            return {}

    @property
    def redirected(self) -> bool:
        """Whether or not the request was redirected."""
        return len(self.urls) > 1

    @property
    def content(self):
        """The raw content received from the request transformed into a string."""
        self.raw_content.seek(0)

        return self.raw_content.read().decode()

    # noinspection PyUnresolvedReferences
    @classmethod
    def from_reply(cls, reply: QtNetwork.QNetworkReply) -> 'Response':
        """Slowly populates a new Response object with data from the request."""
        r = cls()

        reply.metaDataChanged.connect(functools.partial(r._insert_headers, reply.rawHeaderPairs()))
        reply.redirected.connect(r._insert_url)
        reply.error.connect(r._update_code)
        reply.error.connect(functools.partial(r._update_error_string, reply.errorString()))

        signals.wait_for_signal(reply.finished)

        r._from_reply(reply)

        reply.close()
        reply.deleteLater()

        return r

    def _from_reply(self, reply: QtNetwork.QNetworkReply):
        """Updates the Response object with the remaining data from the reply."""
        if reply.isReadable():
            self.raw_content.seek(0)
            self.raw_content.write(reply.readAll())

        manager: QtNetwork.QNetworkAccessManager = reply.manager()
        jar: QtNetwork.QNetworkCookieJar = manager.cookieJar()
        object.__setattr__(self, 'cookies', {c.name().data().decode(): c.value() for c in jar.allCookies()})

    def _insert_headers(self, headers: typing.List[typing.Tuple[QtCore.QByteArray, QtCore.QByteArray]]):
        """Inserts the passed headers into the classes' header list."""
        h = self.all_headers.copy()
        h.append({k.data().decode(): v.data().decode() for k, v in headers})

        object.__setattr__(self, 'all_headers', h)

    def _insert_url(self, url: QtCore.QUrl):
        """Inserts the passed url into the classes' url list."""
        u = self.urls.copy()
        u.append(url)

        object.__setattr__(self, 'urls', u)

    def _update_code(self, code: int):
        """Updates the classes' code with the one passed."""
        object.__setattr__(self, 'code', code)

    def _update_error_string(self, string: str):
        """Updates the classes' error string with the one passed."""
        object.__setattr__(self, 'error_string', string)

    def is_okay(self) -> bool:
        """Whether or not the request was successful."""
        return self.code == QtNetwork.QNetworkReply.NoError

    def json(self, encoder: typing.Callable[[str], dict] = None) -> dict:
        """Converts the reply's body into a JSON object."""
        if encoder is None:
            encoder = json.loads

        return encoder(self.content)

    def __repr__(self):
        return f'<{self.__class__.__name__} url="{self.url.toDisplayString()}" code={self.code}>'
