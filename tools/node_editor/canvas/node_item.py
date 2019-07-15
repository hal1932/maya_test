# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *
from tools.node_editor.canvas.pyside_modules import *


class ConnectionPoint(QObject):

    moved = Signal(QPointF)

    @property
    def pos(self): return self.__pos

    def __init__(self, x, y):
        super(ConnectionPoint, self).__init__()
        self.__pos = QPointF(x, y)

    def move(self, pos):
        # type: (QPointF) -> NoReturn
        self.__pos = pos
        self.moved.emit(pos)


class NodeItem(QGraphicsRectItem):

    def __init__(self, parent=None):
        super(NodeItem, self).__init__(parent)
        self.setRect(0, 0, 50, 30)
        self.setBrush(QBrush(Qt.red))
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.__connections = []

    def set_position(self, x, y):
        rect = self.rect()
        self.setRect(QRectF(x, y, rect.width(), rect.height()))

    def connect(self, dest):
        rect = self.rect()
        p1 = ConnectionPoint(rect.x(), rect.y())
        self.__connections.append(p1)

        rect = dest.rect()
        p2 = ConnectionPoint(rect.x(), rect.y())
        dest.__connections.append(p2)

        return ConnectionItem(p1, p2)

    def mousePressEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        pass

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        pos = e.pos()
        self.set_position(pos.x(), pos.y())

        for p in self.__connections:
            p.move(pos)


class ConnectionItem(QGraphicsLineItem):

    def __init__(self, p1, p2, parent=None):
        # type: (ConnectionPoint, ConnectionPoint) -> NoReturn
        super(ConnectionItem, self).__init__(parent)
        self._p1 = p1
        self._p2 = p2
        self.set_start(p1.pos)
        self.set_end(p2.pos)

        p1.moved.connect(self.set_start)
        p2.moved.connect(self.set_end)

    def set_start(self, point):
        line = self.line()
        line.setP1(point)
        self.setLine(line)

    def set_end(self, point):
        line = self.line()
        line.setP2(point)
        self.setLine(line)

