# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import inspect
from tools.node_editor.views.pyside_modules import *


class GraphicsItemSignal(object):

    def __init__(self, _):
        self.__slots = []

    def connect(self, slot):
        self.__slots.append(slot)

    def emit(self, args):
        for slot in self.__slots:
            slot(args)


class ConnectionPoint(QGraphicsEllipseItem):

    @property
    def pos(self): return self.__pos

    def __init__(self, x, y):
        # type: (float, float) -> NoReturn
        super(ConnectionPoint, self).__init__()
        self.setRect(x - 5, y - 5, 10, 10)
        self.setBrush(QBrush(Qt.white))
        self.__pos = QPointF(x, y)
        self.moved = GraphicsItemSignal(QPointF)

    def move(self, diff):
        # type: (QPointF) -> NoReturn
        x = self.pos.x() + diff.x()
        y = self.pos.y() + diff.y()
        self.pos.setX(x)
        self.pos.setY(y)

        self.setRect(x - 5, y - 5, 10, 10)

        self.moved.emit(self.pos)


class NodeItem(QGraphicsRectItem):

    def __init__(self, parent=None):
        super(NodeItem, self).__init__(parent)
        self.setRect(0, 0, 100, 60)
        self.setBrush(QBrush(Qt.red))
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.__connections = []

    def set_position(self, pos):
        # type: (QPointF) -> NoReturn
        rect = self.rect()
        self.setRect(QRectF(pos.x(), pos.y(), rect.width(), rect.height()))

        diff_x = pos.x() - rect.x()
        diff_y = pos.y() - rect.y()
        diff = QPointF(diff_x, diff_y)

        for p in self.__connections:
            p.move(diff)

    def connect(self, dest):
        # type: (NodeItem) -> ConnectionItem
        rect = self.rect()
        p1 = ConnectionPoint(rect.x() + rect.width(), rect.y() + rect.height() / 2)
        self.__connections.append(p1)

        rect = dest.rect()
        p2 = ConnectionPoint(rect.x(), rect.y() + rect.height() / 2)
        dest.__connections.append(p2)

        conn = ConnectionItem(p1, p2)

        self.scene().addItem(conn)
        self.scene().addItem(p1)
        self.scene().addItem(p2)

        return conn

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        pos = e.pos()
        rect = self.rect()
        pos = QPointF(pos.x() - rect.width() / 2, pos.y() - rect.height() / 2)
        self.set_position(pos)

    def paint(self, painter, item, widget):
        # type: (QPainter, QStyleOptionGraphicsItem, QWidget) -> NoReturn
        if self.isSelected():
            pen = self.pen()
            dashed_pen = QPen(pen.brush(), pen.width(), Qt.DashLine)
            painter.setPen(dashed_pen)
        painter.drawRoundedRect(self.rect(), 5, 5)


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
        # type: (QPointF) -> NoReturn
        line = self.line()
        line.setP1(point)
        self.setLine(line)

    def set_end(self, point):
        # type: (QPointF) -> NoReturn
        line = self.line()
        line.setP2(point)
        self.setLine(line)

