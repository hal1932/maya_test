# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *


class GraphicsItemSignal(object):

    def __init__(self, *_):
        self.__slots = []

    def connect(self, slot):
        self.__slots.append(slot)

    def disconnect(self, slot):
        self.__slots.remove(slot)

    def emit(self, *args):
        for slot in self.__slots:
            slot(*args)


if __name__ == '__main__':
    class Test(object):
        test = GraphicsItemSignal(int)
        test1 = GraphicsItemSignal(int, int)

        def f(self):
            self.test.emit(1)
            self.test1.emit(2, 3)

    t = Test()
    t.test.connect(lambda x: print(x))
    t.test1.connect(lambda x, y: print(x, y))
    t.f()
