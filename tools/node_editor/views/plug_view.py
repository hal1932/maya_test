# coding: utf-8
from __future__ import absolute_import
from typing import *

from gui.pyside_modules import *
from tools.node_editor.views.item_styles import ItemStyles
from tools.node_editor.views.graphics_item_signal import GraphicsItemSignal
from tools.node_editor.nodes.node import Attribute


class _FloatingEdge(object):

    def __init__(self):
        self.__origin = None  # type: PlugView
        self.__dest = None  # type: PlugView
        self.__edge = None  # type: EdgeView

    def open(self, origin):
        # type: (QGraphicsScene, PlugView) -> NoReturn
        self.__dest = PlugView(origin.scene(), None, not origin.is_input)
        self.__dest.setVisible(False)

        if origin.is_input:
            self.__edge = EdgeView(origin.scene(), None, origin)
        else:
            self.__edge = EdgeView(origin.scene(), origin, None)

        self.__origin = origin

    def set_dest_pos(self, pos):
        # type: (QPoint) -> NoReturn
        edge = self.__edge
        origin = self.__origin

        if edge.source == origin:
            edge.set_end(pos)
        elif edge.destination == origin:
            edge.set_start(pos)

    def set_dest_plug(self, plug):
        # type: (PlugView) -> NoReturn
        edge = self.__edge

        if edge is not None and plug not in edge:
            if edge.source is None:
                edge.set_source(plug)
            elif edge.destination is None:
                edge.set_destination(plug)

    def clear_clear_plug(self):
        # type: () -> NoReturn
        edge = self.__edge
        origin = self.__origin

        if edge is not None and origin not in edge:
            if edge.source == origin:
                edge.set_source(None)
            elif edge.destination == origin:
                edge.set_destination(None)

    def close(self):
        # type: () -> EdgeView
        edge = self.__edge
        if edge is None:
            return None

        source = edge.source
        destination = edge.destination
        if source is not None and destination is not None:
            new_edge = source.connect(destination)

        self.__origin.scene().removeItem(edge)

        return new_edge


class PlugView(QGraphicsEllipseItem):

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
        # type: () -> PlugView
        return self.__source

    @property
    def destinations(self):
        # type: () -> Iterable[PlugView]
        return self.__destinations

    @property
    def model(self):
        # type: () -> Attribute
        return self.__model

    __floating_edge = _FloatingEdge()

    def __init__(self, scene, name, is_input, model=None):
        # type: (QGraphicsScene, QPoint, QGraphicsItem, Attribute) -> NoReturn
        super(PlugView, self).__init__(parent=None)

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
        # type: (PlugView) -> EdgeView
        if other.source == self:
            return None

        if len(other.__edges) > 0:
            assert len(other.__edges) == 1
            edge = list(other.__edges)[0]
            other.disconnect(edge)

        # print 'connect: {} -> {}'.format(self.name, other.name)

        new_edge = EdgeView(self.scene(), self, other)

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
        # type: (EdgeView) -> NoReturn
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
        PlugView.__floating_edge.set_dest_plug(self)

    def mouseLeaveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        self.__update_styles()

        # 作成中のエッジの端点に自分が割り当てられてたら、割り当てを解除する
        PlugView.__floating_edge.clear_clear_plug()

    def mousePressEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn

        # エッジの作成を開始する
        PlugView.__floating_edge.open(self)
        PlugView.__floating_edge.set_dest_pos(e.scenePos())

        super(PlugView, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn

        # 作成中のエッジの端点の位置を更新
        PlugView.__floating_edge.set_dest_pos(e.scenePos())

        self.setBrush(ItemStyles.PLUG_BACKGROUND_ACTIVE)
        super(PlugView, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn

        # 作成中のエッジの端点にノードが割り当てられてたら、正式にコネクションを張る
        if not PlugView.__floating_edge.close():
            self.__reset_connection()

        self.__update_styles()
        super(PlugView, self).mouseReleaseEvent(e)

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
        super(PlugView, self).paint(painter, option, widget)

    def __reset_connection(self):
        self.translate(self.pos())

    def __update_styles(self):
        if len(self.__edges) == 0:
            self.setBrush(ItemStyles.PLUG_BACKGROUND_NORMAL)
        else:
            self.setBrush(ItemStyles.PLUG_BACKGROUND_CONNECTED)


class EdgeView(QGraphicsLineItem):

    @property
    def source(self):
        # type: () -> PlugView
        return self.__source

    @property
    def destination(self):
        # type: () -> PlugView
        return self.__destination

    def __init__(self, scene, source=None, destination=None):
        # type: (QGraphicsScene, PlugView, PlugView) -> NoReturn
        super(EdgeView, self).__init__(parent=None)

        scene.addItem(self)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable | QGraphicsLineItem.ItemIsFocusable)
        self.setPen(ItemStyles.CONNECTION_FOREGROUND_NORMAL)
        self.setZValue(ItemStyles.CONNECTION_Z_ORDER)

        self.__source = source
        self.__destination = destination
        self.__selection_bounds = QGraphicsLineItem(parent=None)
        self.__selection_bounds.setPen(ItemStyles.CONNECTION_FOREGROUND_NORMAL_SHAPE)

        self.delete_requested = GraphicsItemSignal(EdgeView)

        if source is not None:
            self.set_start(source.pos())
            source.moved.connect(self.set_start)

        if destination is not None:
            self.set_end(destination.pos())
            destination.moved.connect(self.set_end)

    def __contains__(self, item):
        # type: (PlugView) -> bool
        return self.source == item or self.destination == item

    def __eq__(self, other):
        # type: (EdgeView) -> NoReturn
        if not isinstance(other, EdgeView):
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
        # type: (PlugView) -> NoReturn
        self.__source = source

    def set_destination(self, destination):
        # type: (PlugView) -> NoReturn
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

