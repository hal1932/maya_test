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
        self.__name = name
        self.__node = node
        self.__value = None
        self.__source = None
        self.__destination = None

    def connect(self, other):
        # type: (Attribute) -> NoReturn
        self.__destination = other
        other.__source = self
        print('{}.{} -> {}.{}'.format(self.node.name, self.name, other.node.name, other.name))

    def disconnect(self, other):
        # type: (Attribute) -> NoReturn
        print('{}.{} // {}.{}'.format(self.node.name, self.name, other.node.name, other.name))
        self.__destination = None
        other.__source = None

    def evaluate(self):
        # type: () -> NoReturn
        if self.source is not None:
            self.source.node.evaluate()
            self.value = self.source.value

    def propagate(self):
        # type: () -> NoReturn
        if self.destination is not None:
            self.destination.value = self.value

