# coding: utf-8
from __future__ import absolute_import

from gui.pyside_modules import *


class ItemStyles(object):

    NODE_FOREGROUND_ACTIVE = QPen(QBrush(Qt.black), 1, Qt.DashLine)
    NODE_INITIAL_RECT = QRect(0, 0, 100, 60)
    NODE_CORNER_RADIUS = 5

    PLUG_RECT = QRect(-10, -10, 20, 20)
    PLUG_BACKGROUND_NORMAL = QBrush(Qt.white)
    PLUG_BACKGROUND_ACTIVE = QBrush(Qt.red)
    PLUG_BACKGROUND_TARGET = QBrush(Qt.blue)
    PLUG_BACKGROUND_CONNECTED = QBrush(Qt.lightGray)

    CONNECTION_FOREGROUND_NORMAL = QPen(QBrush(Qt.black), 1)
    CONNECTION_FOREGROUND_NORMAL_SHAPE = QPen(QBrush(Qt.transparent), 10)

    NODE_Z_ORDER = 100
    CONNECTION_Z_ORDER = 200
    PLUG_Z_ORDER = 300
