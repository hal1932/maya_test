# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

from gui.pyside_modules import *


def hline():
    # type: () -> QFrame
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def vline():
    # type: () -> QFrame
    frame = QFrame()
    frame.setFrameShape(QFrame.VLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame

