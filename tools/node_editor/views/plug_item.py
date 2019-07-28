# coding: utf-8
from __future__ import absolute_import
from typing import *

from gui.pyside_modules import *
from tools.node_editor.views.item_styles import ItemStyles
from tools.node_editor.views.graphics_item_signal import GraphicsItemSignal
from tools.node_editor.nodes.node import Attribute


class PlugItem(QGraphicsEllipseItem):

    @property
    def name(self):
        # type: () -> str
        return self.__name

    @property
    def is_input(self):
        # type: () -> bool
        return self.__is_input

    @property
    def source(self):
        # type: () -> PlugItem
        return self.__source

    @property
    def destinations(self):
        # type: () -> Iterable[PlugItem]
        return self.__destinations

    @property
    def model(self):
        # type: () -> Attribute
        return self.__model

    # __edge_candidate = None

    def __init__(self, scene, name, is_input, model=None):
        # type: (QGraphicsScene, QPoint, QGraphicsItem, Attribute) -> NoReturn
        super(PlugItem, self).__init__(parent=None)

        scene.addItem(self)
        self.setRect(ItemStyles.PLUG_RECT)
        self.setBrush(ItemStyles.PLUG_BACKGROUND_NORMAL)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(ItemStyles.PLUG_Z_ORDER)

        self.__name = name
        self.__model = None
        self.__is_input = is_input
        self.__source = None
        self.__destinations = set()
        self.__edges = set()
        self.__is_connection_candidate = False

        self.set_model(model)

        self.moved = GraphicsItemSignal(QPointF)

    def set_model(self, model):
        # type: (Attribute) -> NoReturn
        self.__model = model

    def translate(self, position):
        # type: (QPoint) -> NoReturn
        self.setPos(position)
        self.moved.emit(position)

    def connect(self, other):
        # type: (PlugItem) -> EdgeItem
        if other.source == self:
            return None

        if len(other.__edges) > 0:
            assert len(other.__edges) == 1
            edge = list(other.__edges)[0]
            other.disconnect(edge)

        # print 'connect: {} -> {}'.format(self.name, other.name)

        new_edge = EdgeItem(self.scene(), self, other)

        new_edge.delete_requested.connect(self.disconnect)

        self.__destinations.add(other)
        other.__source = self

        self.__edges.add(new_edge)
        other.__edges.add(new_edge)

        self.__update_styles()
        other.__update_styles()

        self.model.connect(other.model)

        return self.__edges

    def disconnect(self, edge):
        # type: (EdgeItem) -> NoReturn
        if edge not in self.__edges:
            return

        self.scene().removeItem(edge)
        edge.clear()

        self.model.disconnect(edge.destination.model)

        source = edge.source
        if source is not None:
            source.__edges.remove(edge)
            source.__destinations.remove(edge.destination)
            source.__update_styles()

        destination = edge.destination
        if destination is not None:
            destination.__edges.remove(edge)
            destination.__source = None
            destination.__update_styles()

    def mouseOverEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn

        # マウスオーバーされたらハイライト表示
        self.setBrush(ItemStyles.PLUG_BACKGROUND_TARGET)

        # エッジ作成中だったら、そのエッジの端点に自分を割り当てる
        EdgeFactory.set_other_plug(self)

    def mouseLeaveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        self.__update_styles()

        # 作成中のエッジの端点に自分が割り当てられてたら、割り当てを解除する
        EdgeFactory.clear_other_plug()

    def mousePressEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn

        # エッジの作成を開始する
        EdgeFactory.setup(self)
        EdgeFactory.set_other_pos(e.scenePos())

        super(PlugItem, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn

        # 作成中のエッジの端点の位置を更新
        EdgeFactory.set_other_pos(e.scenePos())

        self.setBrush(ItemStyles.PLUG_BACKGROUND_ACTIVE)
        super(PlugItem, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn

        # 作成中のエッジの端点にノードが割り当てられてたら、正式にコネクションを張る
        if not EdgeFactory.commit():
            self.__reset_connection()

        self.__update_styles()
        super(PlugItem, self).mouseReleaseEvent(e)

    def paint(self, painter, option, widget):
        # type: (QPainter, QStyleOptionGraphicsItem, QWidget) -> NoReturn
        fm = QFontMetrics(painter.font())
        label_width = fm.width(self.name)
        label_height = fm.height() - fm.descent()

        rect = self.rect()
        if self.is_input:
            label_pos = QPoint(rect.width() * 0.75, label_height / 2)
        else:
            label_pos = QPoint(-label_width - rect.width() * 0.75, label_height / 2)

        painter.drawText(label_pos, self.name)
        super(PlugItem, self).paint(painter, option, widget)

    def __reset_connection(self):
        self.translate(self.pos())

    def __update_styles(self):
        if len(self.__edges) == 0:
            self.setBrush(ItemStyles.PLUG_BACKGROUND_NORMAL)
        else:
            self.setBrush(ItemStyles.PLUG_BACKGROUND_CONNECTED)


class EdgeFactory(object):

    origin_plug = None
    other_plug = None
    edge = None

    @staticmethod
    def setup(origin):
        # type: (QGraphicsScene, PlugItem) -> NoReturn
        EdgeFactory.other_plug = PlugItem(origin.scene(), None, not origin.is_input)
        EdgeFactory.other_plug.setVisible(False)

        if origin.is_input:
            EdgeFactory.edge = EdgeItem(origin.scene(), None, origin)
        else:
            EdgeFactory.edge = EdgeItem(origin.scene(), origin, None)

        EdgeFactory.origin_plug = origin

    @staticmethod
    def set_other_pos(pos):
        # type: (QPoint) -> NoReturn
        if EdgeFactory.edge.source == EdgeFactory.origin_plug:
            EdgeFactory.edge.set_end(pos)
        elif EdgeFactory.edge.destination == EdgeFactory.origin_plug:
            EdgeFactory.edge.set_start(pos)

    @staticmethod
    def set_other_plug(plug):
        # type: (PlugItem) -> NoReturn
        edge = EdgeFactory.edge

        if edge is not None and plug not in edge:
            if edge.source is None:
                edge.set_source(plug)
            elif edge.destination is None:
                edge.set_destination(plug)

    @staticmethod
    def clear_other_plug():
        # type: () -> NoReturn
        edge = EdgeFactory.edge
        origin = EdgeFactory.origin_plug

        if edge is not None and origin not in edge:
            if edge.source == origin:
                edge.set_source(None)
            elif edge.destination == origin:
                edge.set_destination(None)

    @staticmethod
    def commit():
        # type: () -> bool
        edge = EdgeFactory.edge
        if edge is None:
            return False

        source = edge.source
        destination = edge.destination
        if source is not None and destination is not None:
            source.connect(destination)

        EdgeFactory.origin_plug.scene().removeItem(edge)
        return True


class EdgeItem(QGraphicsLineItem):

    @property
    def source(self):
        # type: () -> PlugItem
        return self.__source

    @property
    def destination(self):
        # type: () -> PlugItem
        return self.__destination

    def __init__(self, scene, source=None, destination=None):
        # type: (QGraphicsScene, PlugItem, PlugItem) -> NoReturn
        super(EdgeItem, self).__init__(parent=None)

        scene.addItem(self)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable | QGraphicsLineItem.ItemIsFocusable)
        self.setPen(ItemStyles.CONNECTION_FOREGROUND_NORMAL)
        self.setZValue(ItemStyles.CONNECTION_Z_ORDER)

        self.__source = source
        self.__destination = destination
        self.__selection_bounds = QGraphicsLineItem(parent=None)
        self.__selection_bounds.setPen(ItemStyles.CONNECTION_FOREGROUND_NORMAL_SHAPE)

        self.delete_requested = GraphicsItemSignal(EdgeItem)

        if source is not None:
            self.set_start(source.pos())
            source.moved.connect(self.set_start)

        if destination is not None:
            self.set_end(destination.pos())
            destination.moved.connect(self.set_end)

    def __contains__(self, item):
        # type: (PlugItem) -> bool
        return self.source == item or self.destination == item

    def __eq__(self, other):
        # type: (EdgeItem) -> NoReturn
        if not isinstance(other, EdgeItem):
            return False
        if other is None:
            return False
        return self.source == other.source and self.destination == other.destination

    def __hash__(self):
        return self.source.__hash__() ^ self.destination.__hash__()

    def clear(self):
        if self.source is not None:
            self.source.moved.disconnect(self.set_start)

        if self.destination is not None:
            self.destination.moved.disconnect(self.set_end)

    def set_source(self, source):
        # type: (PlugItem) -> NoReturn
        self.__source = source

    def set_destination(self, destination):
        # type: (PlugItem) -> NoReturn
        self.__destination = destination

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

