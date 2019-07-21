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

    NODE_Z_ORDER = 100
    CONNECTION_Z_ORDER = 200
    PLUG_Z_ORDER = 300


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


class PlugItem(QGraphicsEllipseItem):

    @property
    def name(self): return self.__name

    @property
    def is_input(self): return self.__is_input

    @property
    def source(self): return self.__source

    @property
    def destination(self): return self.__destination

    __edge_candidate = None

    def __init__(self, scene, name, is_input):
        # type: (QGraphicsScene, QPoint, QGraphicsItem) -> NoReturn
        super(PlugItem, self).__init__(parent=None)

        scene.addItem(self)
        self.setRect(-10, -10, 20, 20)
        self.setBrush(ItemStyles.PLUG_BACKGROUND_NORMAL)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(ItemStyles.PLUG_Z_ORDER)

        self.__name = name
        self.__is_input = is_input
        self.__source = None
        self.__destination = None
        self.__edges = None
        self.__is_connection_candidate = False

        self.moved = GraphicsItemSignal(QPointF)

    def translate(self, position):
        # type: (QPoint) -> NoReturn
        self.setPos(position)
        self.moved.emit(position)

    def connect(self, other):
        # type: (PlugItem) -> EdgeItem
        self.__edges = EdgeItem(self.scene(), self, other)

        def _delete_connection(_):
            self.disconnect()
        self.__edges.delete_requested.connect(_delete_connection)

        self.__destination = other
        other.__source = self
        other.__edges = self.__edges

        self.__update_styles()
        other.__update_styles()

        return self.__edges

    def disconnect(self):
        if self.__edges is not None:
            self.scene().removeItem(self.__edges)
            self.__edges.clear()

            source = self.__edges.source
            destination = self.__edges.destination
            if source is not None:
                source.__connection = None
                source.__update_styles()
            if destination is not None:
                destination.__connection = None
                destination.__update_styles()

            self.__edges = None

    def mouseOverEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        self.setBrush(ItemStyles.PLUG_BACKGROUND_TARGET)

        tmp_edge= PlugItem.__edge_candidate
        if tmp_edge is not None and tmp_edge.parentItem() != self:
            if tmp_edge.source is None:
                tmp_edge.set_source(self)
            elif tmp_edge.destination is None:
                tmp_edge.set_destination(self)

    def mouseLeaveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        self.__update_styles()

        tmp_edge = PlugItem.__edge_candidate
        if tmp_edge is not None and tmp_edge.parentItem() != self:
            if tmp_edge.source == self:
                tmp_edge.set_source(None)
            elif tmp_edge.destination == self:
                tmp_edge.set_destination(None)

    def mousePressEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        tmp_other = PlugItem(self.scene(), None, not self.is_input)
        tmp_other.setVisible(False)
        if self.is_input:
            edge = EdgeItem(self.scene(), self, None)
            edge.set_end(e.scenePos())
        else:
            edge = EdgeItem(self.scene(), None, self)
            edge.set_start(e.scenePos())
        PlugItem.__edge_candidate = edge

        super(PlugItem, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        tmp_edge= PlugItem.__edge_candidate
        if tmp_edge.source == self:
            tmp_edge.set_end(e.scenePos())
        elif tmp_edge.destination == self:
            tmp_edge.set_start(e.scenePos())

        self.setBrush(ItemStyles.PLUG_BACKGROUND_ACTIVE)
        super(PlugItem, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        tmp_edge = PlugItem.__edge_candidate
        if tmp_edge is not None:
            source = tmp_edge.source
            destination = tmp_edge.destination
            if source is not None and destination is not None:
                source.connect(destination)

            self.scene().removeItem(tmp_edge)
            PlugItem.__edge_candidate = None
        else:
            self.__reset_connection()

        self.__update_styles()
        super(PlugItem, self).mouseReleaseEvent(e)

    def __reset_connection(self):
        self.translate(self.pos())

    def __update_styles(self):
        if self.__edges is None:
            self.setBrush(ItemStyles.PLUG_BACKGROUND_NORMAL)
        else:
            self.setBrush(ItemStyles.PLUG_BACKGROUND_CONNECTED)


class NodeItem(QGraphicsRectItem):

    @property
    def name(self): return self.__name

    def __init__(self, scene, name):
        # type: (QGraphicsScene, str) -> NoReturn
        super(NodeItem, self).__init__(parent=None)

        scene.addItem(self)

        self.setRect(ItemStyles.NODE_RECT)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.setZValue(ItemStyles.NODE_Z_ORDER)

        self.__name = name
        self.__source_plugs = []
        self.__dest_plugs = []

    def set_position(self, pos):
        # type: (QPoint) -> NoReturn
        rect = self.rect()

        w = rect.width()
        h = rect.height()
        x = pos.x() - w / 2
        y = pos.y() - h / 2
        self.setPos(x, y)

        self.__align_source_plugs()
        self.__align_dest_plugs()

    def add_input(self, name):
        # type: (str) -> PlugItem
        plug = PlugItem(self.scene(), name, True)
        self.__source_plugs.append(plug)
        self.__align_source_plugs()
        return plug

    def add_output(self, name):
        # type: (str) -> PlugItem
        plug = PlugItem(self.scene(), name, False)
        self.__dest_plugs.append(plug)
        self.__align_dest_plugs()
        return plug

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        delta = e.pos() - e.lastPos()

        pos = self.pos() + self.rect().center() + delta
        self.set_position(QPoint(pos.x(), pos.y()))

        super(NodeItem, self).mouseMoveEvent(e)

    def paint(self, painter, item, widget):
        # type: (QPainter, QStyleOptionGraphicsItem, QWidget) -> NoReturn
        if self.isSelected():
            painter.setPen(ItemStyles.NODE_FOREGROUND_ACTIVE)
        painter.drawRoundedRect(self.rect(), ItemStyles.NODE_CORNER_RADIUS, ItemStyles.NODE_CORNER_RADIUS)

    def __align_source_plugs(self):
        pos = self.pos()
        rect = self.rect()

        x = pos.x()

        y_base = pos.y()
        y_offset = rect.height() / float(len(self.__source_plugs) + 1)

        for i, plug in enumerate(self.__source_plugs):
            y = y_base + y_offset * (i + 1)
            plug.translate(QPoint(x, y))

    def __align_dest_plugs(self):
        pos = self.pos()
        rect = self.rect()

        x = pos.x() + rect.width()

        y_base = pos.y()
        y_offset = rect.height() / float(len(self.__dest_plugs) + 1)

        for i, plug in enumerate(self.__dest_plugs):
            y = y_base + y_offset * (i + 1)
            plug.translate(QPoint(x, y))


class EdgeItem(QGraphicsLineItem):

    @property
    def source(self): return self.__p1

    @property
    def destination(self): return self.__p2

    def __init__(self, scene, p1=None, p2=None):
        # type: (QGraphicsScene, PlugItem, PlugItem) -> NoReturn
        super(EdgeItem, self).__init__(parent=None)

        scene.addItem(self)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable | QGraphicsLineItem.ItemIsFocusable)
        self.setPen(ItemStyles.CONNECTION_FOREGROUND_NORMAL)
        self.setZValue(ItemStyles.CONNECTION_Z_ORDER)

        self.__p1 = p1
        self.__p2 = p2
        self.__selection_bounds = QGraphicsLineItem(parent=None)
        self.__selection_bounds.setPen(ItemStyles.CONNECTION_FOREGROUND_NORMAL_SHAPE)

        self.delete_requested = GraphicsItemSignal(EdgeItem)

        if p1 is not None:
            self.set_start(p1.pos())
            p1.moved.connect(self.set_start)

        if p2 is not None:
            self.set_end(p2.pos())
            p2.moved.connect(self.set_end)

    def clear(self):
        if self.source is not None:
            self.source.moved.disconnect(self.set_start)

        if self.destination is not None:
            self.destination.moved.disconnect(self.set_end)

    def set_source(self, source):
        # type: (PlugItem) -> NoReturn
        self.__p1 = source

    def set_destination(self, destination):
        # type: (PlugItem) -> NoReturn
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

