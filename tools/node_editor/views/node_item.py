# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

from tools.node_editor.views.pyside_modules import *
from tools.node_editor.views.item_styles import ItemStyles
from tools.node_editor.views.plug_item import PlugItem


class NodeItem(QGraphicsRectItem):

    @property
    def name(self): return self.__name

    def __init__(self, scene, name):
        # type: (QGraphicsScene, str) -> NoReturn
        super(NodeItem, self).__init__(parent=None)

        scene.addItem(self)

        self.setRect(ItemStyles.NODE_INITIAL_RECT)
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
        self.__update_rect()
        self.__align_source_plugs()
        return plug

    def add_output(self, name):
        # type: (str) -> PlugItem
        plug = PlugItem(self.scene(), name, False)
        self.__dest_plugs.append(plug)
        self.__update_rect()
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
        fm = QFontMetrics(painter.font())
        label_width = fm.width(self.name)

        rect = self.rect()
        label_pos = QPoint(rect.x() + rect.width() / 2 - label_width / 2, rect.y() - fm.descent())
        painter.drawText(label_pos, self.name)

        if self.isSelected():
            painter.setPen(ItemStyles.NODE_FOREGROUND_ACTIVE)
        painter.drawRoundedRect(self.rect(), ItemStyles.NODE_CORNER_RADIUS, ItemStyles.NODE_CORNER_RADIUS)

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


