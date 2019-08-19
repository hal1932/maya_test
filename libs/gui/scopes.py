# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

from libs.gui.pyside_modules import *


class WaitCursorScope(object):

    def __enter__(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def __exit__(self, exc_type, exc_val, exc_tb):
        QApplication.restoreOverrideCursor()


def wait_cursor_scope(func):
    def _(*args, **kwargs):
        with WaitCursorScope():
            func(*args, **kwargs)
    return _
