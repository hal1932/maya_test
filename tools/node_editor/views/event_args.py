# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *


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

