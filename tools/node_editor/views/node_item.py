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

    z_order = 20

    @property
    def pos(self): return self.__pos

    @property
    def source(self): return self.__source

    @property
    def destination(self): return self.__destination

    def __init__(self, x, y):
        # type: (float, float) -> NoReturn
        super(ConnectionPoint, self).__init__()
        self.setRect(x - 10, y - 10, 20, 20)
        self.setBrush(QBrush(Qt.white))
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.setZValue(ConnectionPoint.z_order)
        self.__pos = QPointF(x, y)
        self.__source = None
        self.__destination = None
        self.moved = GraphicsItemSignal(QPointF)

    def move(self, diff):
        # type: (QPointF) -> NoReturn
        x = self.pos.x() + diff.x()
        y = self.pos.y() + diff.y()
        self.pos.setX(x)
        self.pos.setY(y)

        self.setRect(x - 10, y - 10, 20, 20)

        self.moved.emit(self.pos)

    def connect(self, other):
        # type: (ConnectionPoint) -> ConnectionItem
        conn = ConnectionItem(self, other)
        self.scene().addItem(conn)

        self.__destination = other
        other.__source = self

        return conn

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        if self.source is None and self.destination is None:
            self.move(e.pos() - e.lastPos())
        super(ConnectionPoint, self).mouseMoveEvent(e)


class NodeItem(QGraphicsRectItem):

    z_order = 0

    def __init__(self, parent=None):
        super(NodeItem, self).__init__(parent)
        self.setRect(0, 0, 100, 60)
        self.setBrush(QBrush(Qt.red))
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.setZValue(NodeItem.z_order)
        self.__connections = []

    def set_position(self, pos):
        # type: (QPointF) -> NoReturn
        rect = self.rect()

        w = rect.width()
        h = rect.height()
        x = pos.x() - w / 2
        y = pos.y() - h / 2
        self.setRect(QRectF(x, y, w, h))

        diff_x = x - rect.x()
        diff_y = y - rect.y()
        diff = QPointF(diff_x, diff_y)

        for p in self.__connections:
            p.move(diff)

    def set_input(self, name):
        # type: (str) -> ConnectionPoint
        rect = self.rect()
        point = ConnectionPoint(rect.x(), rect.y() + rect.height() / 2)
        self.__connections.append(point)
        self.scene().addItem(point)
        return point

    def set_output(self, name):
        # type: (str) -> ConnectionPoint
        rect = self.rect()
        point = ConnectionPoint(rect.x() + rect.width(), rect.y() + rect.height() / 2)
        self.__connections.append(point)
        self.scene().addItem(point)
        return point

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        delta = e.pos() - e.lastPos()

        pos = self.rect().center() + delta
        self.set_position(pos)

        super(NodeItem, self).mouseMoveEvent(e)

    def paint(self, painter, item, widget):
        # type: (QPainter, QStyleOptionGraphicsItem, QWidget) -> NoReturn
        if self.isSelected():
            pen = self.pen()
            dashed_pen = QPen(pen.brush(), pen.width(), Qt.DashLine)
            painter.setPen(dashed_pen)
        painter.drawRoundedRect(self.rect(), 5, 5)


class ConnectionItem(QGraphicsLineItem):

    z_order = 10

    def __init__(self, p1, p2, parent=None):
        # type: (ConnectionPoint, ConnectionPoint) -> NoReturn
        super(ConnectionItem, self).__init__(parent)
        self.setZValue(ConnectionItem.z_order)
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

