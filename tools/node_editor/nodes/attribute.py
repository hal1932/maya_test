# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *


class Attribute(object):

    @property
    def node(self):
        # type: () -> Node
        return self.__node

    @property
    def name(self):
        # type: () -> str
        return self.__name

    @property
    def value(self):
        # type: () -> object
        return self.__value

    @value.setter
    def value(self, value):
        # type: (object) -> NoReturn
        self.__value = value
        self.set_dirty()

    @property
    def source(self):
        # type: () -> Attribute
        return self.__source

    @property
    def destination(self):
        # type: () -> Attribute
        return self.__destination

    def __init__(self, name, node):
        # type: (str, Node) -> NoReturn
        self.__name = name  # type: str
        self.__node = node  # type: Node
        self.__value = None  # type: object
        self.__source = None  # type: Attribute
        self.__destination = None  # type: Attribute
        self.__is_dirty = True  # type: bool
        self.__affect_destination = None  # type: Attribute

    def connect(self, other):
        # type: (Attribute) -> NoReturn
        self.__destination = other
        self.__destination.set_dirty()
        other.__source = self

    def disconnect(self, other):
        # type: (Attribute) -> NoReturn
        self.__destination = None
        other.__source = None

    def evaluate(self):
        # type: () -> NoReturn
        if not self.__is_dirty:
            return

        if self.source is not None:
            self.source.node.evaluate()
            self.value = self.source.value

        self.__is_dirty = False

    def propagate(self):
        # type: () -> NoReturn
        if self.destination is not None:
            self.destination.value = self.value

    def set_dirty(self):
        # type: () -> NoReturn
        self.__is_dirty = True
        if self.__affect_destination is not None:
            self.__affect_destination.set_dirty()
        if self.destination is not None:
            self.destination.set_dirty()

    def _set_affect(self, dest):
        # type: (Attribute) -> NoReturn
        self.__affect_destination = dest

