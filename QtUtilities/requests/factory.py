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
from typing import AnyStr, Dict, Optional, TYPE_CHECKING, Union

from PySide6 import QtCore, QtNetwork

from .response import Response

if TYPE_CHECKING:
    URL: Union[QtCore.QUrl, str]
    DATA: Union[str, bytes, QtCore.QBuffer]
    HEADERS: Dict[AnyStr, AnyStr]
    PARAMS: Dict[str, str]

__all__ = ['Factory']


class Factory(QtCore.QObject):
    """The core of the requests package.

    This class is responsible for issuing requests through the application's
    QNetworkAccessManager, and returning the response in a synchronous way."""

    def __init__(self, manager: QtNetwork.QNetworkAccessManager = None, *, parent: QtCore.QObject = None):
        super(Factory, self).__init__(parent=parent)

        self._manager = manager if manager is not None else QtNetwork.QNetworkAccessManager(parent=self)

    def request(self, op: str, url: URL = None, *, params: PARAMS = None, headers: HEADERS = None, data: DATA = None,
                request: QtNetwork.QNetworkRequest = None):
        """Issues a new request.

        This method was designed to mimic standard synchronous libraries on PyPi,
        but on the Qt event loop.

        :param op: The HTTP operation to perform.
        :param url: The url to send the request to.
        :param params: A dictionary of parameters to stitch onto the end of the
                       url.
        :param headers: A dictionary of headers to send along with the request.
        :param data: The data to send along with the request.
        :param request: A standalone QNetworkRequest object to use instead of
                        the data provided through the other parameters."""
        if request is not None:
            return self._request(op.upper(), request, data=data)

        request = QtNetwork.QNetworkRequest()
        url: QtCore.QUrl = url if not isinstance(url, str) else QtCore.QUrl(url)

        request.setUrl(url)

        if params is not None:
            url.setQuery(self._build_query(params))

        if headers is not None:
            self._build_headers(headers, request)

        buffer: Optional[QtCore.QBuffer] = None
        if data is not None and not isinstance(data, QtCore.QBuffer):
            buffer = QtCore.QBuffer()

            if isinstance(data, str):
                buffer.setData(QtCore.QByteArray(data.encode(encoding='UTF-8')))

            elif isinstance(data, bytes):
                buffer.setData(QtCore.QByteArray(data))

        return self._request(op.upper(), request, data=buffer)

    @staticmethod
    def _build_headers(headers, request):
        for k, v in headers.items():
            key, value = None, None

            if not isinstance(k, bytes):
                key = k.encode(encoding='UTF-8')

            if not isinstance(v, bytes):
                value = v.encode(encoding='UTF-8')

            request.setRawHeader(QtCore.QByteArray(key), QtCore.QByteArray(value))

    @staticmethod
    def _build_query(params):
        q = QtCore.QUrlQuery()
        for k, v in params.items():
            q.addQueryItem(k, v)
        return q

    def _request(self, op: str, request: QtNetwork.QNetworkRequest, *, data: QtCore.QBuffer = None):
        """The real implementation of the request method."""
        # Send the request & return the Response object
        return Response.from_reply(
            self._manager.sendCustomRequest(
                request,
                QtCore.QByteArray(op.encode(encoding='UTF-8')),
                data
            )
        )

    def get(self, url: URL = None, *, params: PARAMS = None, headers: HEADERS = None,
            request: QtNetwork.QNetworkRequest = None):
        return self.request('GET', url=url, params=params, headers=headers, request=request)

    def put(self, url: URL = None, *, params: PARAMS = None, headers: HEADERS = None,
            request: QtNetwork.QNetworkRequest = None):
        return self.request('PUT', url=url, params=params, headers=headers, request=request)

    def post(self, url: URL = None, *, params: PARAMS = None, headers: HEADERS = None, data: DATA = None,
             request: QtNetwork.QNetworkRequest = None):
        return self.request('POST', url=url, params=params, headers=headers, data=data, request=request)

    def head(self, url: URL = None, *, params: PARAMS = None, headers: HEADERS = None,
             request: QtNetwork.QNetworkRequest = None):
        return self.request('HEAD', url=url, params=params, headers=headers, request=request)

    def patch(self, url: URL = None, *, params: PARAMS = None, headers: HEADERS = None,
              request: QtNetwork.QNetworkRequest = None):
        return self.request('PATCH', url=url, params=params, headers=headers, request=request)

    def delete(self, url: URL = None, *, params: PARAMS = None, headers: HEADERS = None,
               request: QtNetwork.QNetworkRequest = None):
        return self.request('DELETE', url=url, params=params, headers=headers, request=request)

    def options(self, url: URL = None, *, params: PARAMS = None, headers: HEADERS = None,
                request: QtNetwork.QNetworkRequest = None):
        return self.request('OPTIONS', url=url, params=params, headers=headers, request=request)
