# coding: utf-8
from __future__ import absolute_import
from typing import *

from gui.pyside_modules import *
from tools.node_editor.views.item_styles import ItemStyles
from tools.node_editor.views.plug_view import PlugView
from tools.node_editor.nodes.node import Node


class NodeView(QGraphicsRectItem):

    @property
    def name(self): return self.__name

    @property
    def model(self): return self.__model

    def __init__(self, scene, name, model=None):
        # type: (QGraphicsScene, str, Node) -> NoReturn
        super(NodeView, self).__init__(parent=None)

        self.__name = name
        self.__model = None
        self.__source_plugs = []
        self.__dest_plugs = []
        self.__bounding_rect = QRectF(ItemStyles.NODE_INITIAL_RECT)

        scene.addItem(self)

        self.set_model(model)

        self.setRect(ItemStyles.NODE_INITIAL_RECT)
        self.setFlags(QGraphicsRectItem.ItemIsSelectable)
        self.setZValue(ItemStyles.NODE_Z_ORDER)

    def set_model(self, model):
        # type: (Node) -> NoReturn
        self.__model = model

        if model is not None:
            for input in model.inputs:
                plug = self.add_input(input.name)
                plug.set_model(input)

            for output in model.outputs:
                plug = self.add_output(output.name)
                plug.set_model(output)

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
        # type: (str) -> PlugView
        plug = PlugView(self.scene(), name, True)
        self.__source_plugs.append(plug)
        self.__update_rect()
        self.__align_source_plugs()
        return plug

    def add_output(self, name):
        # type: (str) -> PlugView
        plug = PlugView(self.scene(), name, False)
        self.__dest_plugs.append(plug)
        self.__update_rect()
        self.__align_dest_plugs()
        return plug

    def contextMenuEvent(self, e):
        # type: (QGraphicsSceneContextMenuEvent) -> NoReturn
        menu = QMenu()
        menu.addAction(self.name)
        action = menu.exec_(e.screenPos())
        if action is not None:
            print(action.text())

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn
        delta = e.pos() - e.lastPos()

        pos = self.pos() + self.rect().center() + delta
        self.set_position(QPoint(pos.x(), pos.y()))

        super(NodeView, self).mouseMoveEvent(e)

    def boundingRect(self):
        # type: () -> QRectF
        return self.__bounding_rect

    def paint(self, painter, item, widget):
        # type: (QPainter, QStyleOptionGraphicsItem, QWidget) -> NoReturn
        label = '{} ({})'.format(self.name, self.__model.name)
        fm = QFontMetrics(painter.font())
        label_width = fm.width(label)

        rect = self.rect()
        label_pos = QPoint(rect.x() + rect.width() / 2 - label_width / 2, rect.y() - fm.descent())
        painter.drawText(label_pos, label)

        if self.isSelected():
            painter.setPen(ItemStyles.NODE_FOREGROUND_ACTIVE)
        painter.drawRoundedRect(self.rect(), ItemStyles.NODE_CORNER_RADIUS, ItemStyles.NODE_CORNER_RADIUS)

        self.__bounding_rect.setRect(rect.x(), rect.y() - fm.height(), rect.width(), rect.height() + fm.height())

    def __update_rect(self):
        plug_count = max(len(self.__source_plugs), len(self.__dest_plugs))
        new_height = plug_count * ItemStyles.PLUG_RECT.height() * 1.5
        new_height = max(new_height, ItemStyles.NODE_INITIAL_RECT.height())

        rect = self.rect()
        rect.setHeight(new_height)
        self.setRect(rect)

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


