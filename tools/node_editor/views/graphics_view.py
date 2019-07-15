# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *
from tools.node_editor.views.pyside_modules import *


class EventArgs(object):

    @property
    def handled(self): return self.__handled

    @handled.setter
    def handled(self, value): self.__handled = value

    def __init__(self):
        self.__handled = False


class MouseMoveEventArgs(EventArgs):

    @property
    def pos(self): return self.__ev.pos()

    @property
    def delta_pos(self): return self.__delta_pos

    @property
    def buttons(self): return self.__ev.buttons

    def __init__(self, e, delta_pos):
        # type: (QMouseEvent, QPointF) -> NoReturn
        super(MouseMoveEventArgs, self).__init__()
        self.__ev = e
        self.__delta_pos = delta_pos


class MouseWheelEventArgs(EventArgs):

    @property
    def delta(self): return self.__delta

    def __init__(self, e):
        # type: (QWheelEvent) -> NoReturn
        super(MouseWheelEventArgs, self).__init__()
        self.__delta = e.delta()


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
