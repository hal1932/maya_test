# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *


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
