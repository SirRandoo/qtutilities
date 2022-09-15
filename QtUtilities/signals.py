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

from PySide6 import QtCore

__all__ = ['wait_for_signal', 'wait_for_signal_or', 'wait_for_signal_and']

logger = logging.getLogger(__name__)


def wait_for_signal(signal, *, timeout: int = None):
    """Waits for `signal`.  If `timeout is specified,
    this method will stop after `timeout` milliseconds.
    :param signal: The signal to wait for.
    :param timeout: The amount of milliseconds to wait
    before timing out."""
    loop = QtCore.QEventLoop()
    timer = QtCore.QTimer()
    emitted = False
    returnables = None

    def on_emit(*args):
        emitted = True
        returnables = args

    try:
        signal.connect(on_emit)
        signal.connect(loop.quit)

        if timeout is not None and timeout > 0:
            timer.singleShot(timeout, loop.quit)

        loop.exec()

    except Exception as e:
        logger.warning("`wait_for_signal` ended abruptly! ({})".format(str(e)))

    finally:
        if loop.isRunning():
            loop.quit()

        if timer.isActive():
            timer.stop()

        loop.deleteLater()
        timer.deleteLater()

    return emitted, returnables


def wait_for_signal_and(*signals, timeout: int = None):
    """Waits for all of the signals passed to be emitted.
    If `timeout` is specified, this method will stop after
    `timeout` milliseconds.
    :param timeout: The amount of milliseconds to wait
    before timing out.

    :returns bool: Whether or not the signal emitted."""
    loop = QtCore.QEventLoop()
    timer = QtCore.QTimer()
    emitted = {str(i): dict() for i, _ in enumerate(signals)}

    try:
        for signal in signals:
            if hasattr(signal, "connect"):
                signal.connect(lambda s: emitted.__setitem__(str(signals.index(s)), True))
                signal.connect(loop.quit)

        if timeout is not None and timeout > 0:
            timer.singleShot(timeout, loop.quit)

        loop.exec()

    except Exception as e:
        logger.warning("`wait_for_signal_and` ended abruptly! ({})".format(str(e)))

    finally:
        if loop.isRunning():
            loop.quit()

        if timer.isActive():
            timer.stop()

        timer.deleteLater()
        loop.deleteLater()

    return all(emitted.values())


def wait_for_signal_or(*signals, timeout: int = None):
    """Waits for one of the signals passed to be emitted.
    If `timeout` is specified, this method will stop after
    `timeout` milliseconds.
    :param timeout: The amount of milliseconds to wait
    before timing out.

    :returns bool: Whether or not the signal emitted."""
    loop = QtCore.QEventLoop()
    timer = QtCore.QTimer()
    emitted = False

    def on_emit():
        emitted = True

    try:
        for signal in signals:
            if hasattr(signal, "connect"):
                signal.connect(on_emit)
                signal.connect(loop.quit)

        if timeout is not None and timeout > 0:
            timer.singleShot(timeout, loop.quit)

        loop.exec()

    except Exception as e:
        logger.warning("`wait_for_signal_or` ended abruptly! ({})".format(str(e)))

    finally:
        if loop.isRunning():
            loop.quit()

        if timer.isActive():
            timer.stop()

        timer.deleteLater()
        loop.deleteLater()

    return emitted
