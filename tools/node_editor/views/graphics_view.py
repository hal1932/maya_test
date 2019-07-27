# coding: utf-8
from __future__ import absolute_import
from typing import *

from gui.pyside_modules import *
from tools.node_editor.views.event_args import MouseMoveEventArgs, MouseWheelEventArgs


class GraphicsView(QGraphicsView):

    mouse_move = Signal(MouseMoveEventArgs)
    mouse_wheel = Signal(MouseWheelEventArgs)

    @property
    def is_alt_key_pressed(self):
        # type: () -> bool
        return self.__keys[Qt.ALT]

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.__keys = {Qt.ALT: False}
        self.__mouse_pos = QPointF(0, 0)

    def mousePressEvent(self, e):
        # type: (QMouseEvent) -> NoReturn
        self.__mouse_pos = e.pos()
        super(GraphicsView, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        # type: (QMouseEvent) -> NoReturn
        pos = e.pos()
        delta_pos = QPointF(pos.x() - self.__mouse_pos.x(), pos.y() - self.__mouse_pos.y())
        move = MouseMoveEventArgs(e, delta_pos)
        self.__mouse_pos = pos

        self.mouse_move.emit(move)

        if not move.handled:
            super(GraphicsView, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        # type: (QMouseEvent) -> NoReturn
        self.__mouse_pos = e.pos()
        super(GraphicsView, self).mouseReleaseEvent(e)

    def wheelEvent(self, e):
        # type: (QWheelEvent) -> NoReturn
        wheel = MouseWheelEventArgs(e)
        self.mouse_wheel.emit(wheel)

        if not wheel.handled:
            super(GraphicsView, self).wheelEvent(e)

    def keyPressEvent(self, e):
        # type: (QKeyEvent) -> NoReturn
        self.__capture_modifier_keys(e.modifiers())
        super(GraphicsView, self).keyPressEvent(e)

    def keyReleaseEvent(self, e):
        # type: (QKeyEvent) -> NoReturn
        self.__capture_modifier_keys(e.modifiers())
        super(GraphicsView, self).keyReleaseEvent(e)

    def __capture_modifier_keys(self, modifiers):
        self.__keys[Qt.ALT] = modifiers and Qt.AltModifier
