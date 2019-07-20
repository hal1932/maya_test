# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import inspect
from tools.node_editor.views.pyside_modules import *


class ItemStyles(object):

    NODE_FOREGROUND_ACTIVE = QPen(QBrush(Qt.black), 1, Qt.DashLine)
    NODE_RECT = QRect(0, 0, 100, 60)
    NODE_CORNER_RADIUS = 5

    PLUG_BACKGROUND_NORMAL = QBrush(Qt.white)
    PLUG_BACKGROUND_ACTIVE = QBrush(Qt.red)
    PLUG_BACKGROUND_TARGET = QBrush(Qt.blue)
    PLUG_BACKGROUND_CONNECTED = QBrush(Qt.lightGray)

    CONNECTION_FOREGROUND_NORMAL = QPen(QBrush(Qt.black), 1)
    CONNECTION_FOREGROUND_NORMAL_SHAPE = QPen(QBrush(Qt.transparent), 10)


class GraphicsItemSignal(object):

    def __init__(self, _):
        self.__slots = []

    def connect(self, slot):
        self.__slots.append(slot)

    def disconnect(self, slot):
        self.__slots.remove(slot)

    def emit(self, args):
        for slot in self.__slots:
            slot(args)


class ConnectionPoint(QGraphicsEllipseItem):

    z_order = 20

    @property
    def name(self): return self.__name

    @property
    def pos(self): return self.__pos

    @property
    def source(self): return self.__source

    @property
    def destination(self): return self.__destination

    @property
    def is_source(self): return self.destination is not None

    @property
    def is_destination(self): return self.source is not None

    __connection_candidate = None

    def __init__(self, name, position, parent=None):
        # type: (QPoint, QGraphicsItem) -> NoReturn
        super(ConnectionPoint, self).__init__(parent)
        self.setRect(position.x() - 10, position.y() - 10, 20, 20)
        self.setBrush(ItemStyles.PLUG_BACKGROUND_NORMAL)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.setZValue(ConnectionPoint.z_order)
        self.setAcceptHoverEvents(True)
        self.__name = name
        self.__pos = position
        self.__source = None
        self.__destination = None
        self.__connection = None
        self.__is_connection_candidate = False
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
        self.__connection = ConnectionItem(self, other)
        self.scene().addItem(self.__connection)

        def _delete_connection(_):
            self.disconnect()
        self.__connection.delete_requested.connect(_delete_connection)

        self.__destination = other
        other.__source = self
        other.__connection = self.__connection

        self.__update_styles()
        other.__update_styles()

        return self.__connection

    def disconnect(self):
        if self.__connection is not None:
            self.scene().removeItem(self.__connection)
            self.__connection.clear()

            source = self.__connection.source
            destination = self.__connection.destination
            if source is not None:
                source.__connection = None
                source.__update_styles()
            if destination is not None:
                destination.__connection = None
                destination.__update_styles()

            self.__connection = None

    def mouseOverEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        self.setBrush(ItemStyles.PLUG_BACKGROUND_TARGET)

        conn = ConnectionPoint.__connection_candidate
        if conn is not None and conn.parentItem() != self:
            if conn.source is None:
                conn.set_source(self)
            elif conn.destination is None:
                conn.set_destination(self)

    def mouseLeaveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        self.__update_styles()

        conn = ConnectionPoint.__connection_candidate
        if conn is not None and conn.parentItem() != self:
            if conn.source == self:
                conn.set_source(None)
            elif conn.destination == self:
                conn.set_destination(None)

    def mousePressEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        if self.__connection is None:
            tmp_other = ConnectionPoint(None, e.pos())
            tmp_other.setVisible(False)
            if self.is_source:
                conn = ConnectionItem(self, None)
                conn.set_start(self.pos)
                conn.set_end(e.pos())
            else:
                conn = ConnectionItem(None, self)
                conn.set_start(e.pos())
                conn.set_end(self.pos)
            self.scene().addItem(conn)
            conn.setParentItem(self)
            ConnectionPoint.__connection_candidate = conn

        super(ConnectionPoint, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        if self.__connection is None:
            conn = ConnectionPoint.__connection_candidate
            if conn.parentItem() == self:
                if conn.source == self:
                    conn.set_end(e.pos())
                elif conn.destination == self:
                    conn.set_start(e.pos())
        else:
            if self.is_source:
                self.__connection.set_start(e.pos())
            elif self.is_destination:
                self.__connection.set_end(e.pos())

        self.setBrush(ItemStyles.PLUG_BACKGROUND_ACTIVE)
        super(ConnectionPoint, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        conn = ConnectionPoint.__connection_candidate
        if conn is not None:
            source = conn.source
            destination = conn.destination
            if source is not None and destination is not None:
                source.connect(destination)

            self.scene().removeItem(conn)
            ConnectionPoint.__connection_candidate = None
        else:
            self.__reset_connection()

        self.__update_styles()
        super(ConnectionPoint, self).mouseReleaseEvent(e)

    def __reset_connection(self):
        self.move(QPoint(0, 0))

    def __update_styles(self):
        if self.__connection is None:
            self.setBrush(ItemStyles.PLUG_BACKGROUND_NORMAL)
        else:
            self.setBrush(ItemStyles.PLUG_BACKGROUND_CONNECTED)


class NodeItem(QGraphicsRectItem):

    z_order = 0

    @property
    def name(self): return self.__name

    def __init__(self, name, parent=None):
        super(NodeItem, self).__init__(parent)
        self.setRect(ItemStyles.NODE_RECT)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.setZValue(NodeItem.z_order)
        self.__name = name
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
        point = ConnectionPoint(name, QPoint(rect.x(), rect.y() + rect.height() / 2))
        self.__connections.append(point)
        self.scene().addItem(point)
        return point

    def set_output(self, name):
        # type: (str) -> ConnectionPoint
        rect = self.rect()
        point = ConnectionPoint(name, QPoint(rect.x() + rect.width(), rect.y() + rect.height() / 2))
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
            painter.setPen(ItemStyles.NODE_FOREGROUND_ACTIVE)
        painter.drawRoundedRect(self.rect(), ItemStyles.NODE_CORNER_RADIUS, ItemStyles.NODE_CORNER_RADIUS)


class ConnectionItem(QGraphicsLineItem):

    z_order = 10

    @property
    def source(self): return self.__p1

    @property
    def destination(self): return self.__p2

    def __init__(self, p1=None, p2=None, parent=None):
        # type: (ConnectionPoint, ConnectionPoint) -> NoReturn
        super(ConnectionItem, self).__init__(parent)
        self.setZValue(ConnectionItem.z_order)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable | QGraphicsLineItem.ItemIsFocusable)
        self.setPen(ItemStyles.CONNECTION_FOREGROUND_NORMAL)

        self.delete_requested = GraphicsItemSignal(ConnectionItem)

        self.__p1 = p1
        self.__p2 = p2
        self.__selection_bounds = QGraphicsLineItem()
        self.__selection_bounds.setPen(ItemStyles.CONNECTION_FOREGROUND_NORMAL_SHAPE)

        if p1 is not None:
            self.set_start(p1.pos)
            p1.moved.connect(self.set_start)

        if p2 is not None:
            self.set_end(p2.pos)
            p2.moved.connect(self.set_end)

    def clear(self):
        if self.source is not None:
            self.source.moved.disconnect(self.set_start)

        if self.destination is not None:
            self.destination.moved.disconnect(self.set_end)

    def set_source(self, source):
        # type: (ConnectionPoint) -> NoReturn
        self.__p1 = source

    def set_destination(self, destination):
        # type: (ConnectionPoint) -> NoReturn
        self.__p2 = destination

    def set_start(self, point):
        # type: (QPointF) -> NoReturn
        line = self.line()
        line.setP1(point)
        self.setLine(line)
        self.__selection_bounds.setLine(self.line())

    def set_end(self, point):
        # type: (QPointF) -> NoReturn
        line = self.line()
        line.setP2(point)
        self.setLine(line)
        self.__selection_bounds.setLine(self.line())

    def keyReleaseEvent(self, e):
        # type: (QKeyEvent) -> NoReturn
        if self.isSelected() and e.key() == Qt.Key_Delete:
            self.delete_requested.emit(self)

    def shape(self):
        path = QPainterPath()
        path.addPath(self.__selection_bounds.shape())
        return path

