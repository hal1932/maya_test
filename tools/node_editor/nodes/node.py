# coding: utf-8
from __future__ import absolute_import
from typing import *
from six import add_metaclass
from six.moves import *

from abc import ABCMeta, abstractmethod


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
        # type: (Attribute) -> Attribute
        self.__destination = other
        other.__source = self

    def propagate(self):
        # type: () -> bool
        if self.__destination is None:
            return False
        self.__destination.value = self.value
        return True


@add_metaclass(ABCMeta)
class Node(object):

    @property
    def name(self):
        # type: () -> str
        return self.__name

    @property
    def data(self):
        # type: () -> object
        """DataBlock"""
        return self.__data

    @data.setter
    def data(self, value):
        # type: (object) -> NoReturn
        """DataBlock"""
        self.__data = value

    @property
    def inputs(self):
        # type: () -> Iterable[Attribute]
        return self.__inputs.values()

    @property
    def outputs(self):
        # type: () -> Iterable[Attribute]
        return self.__outputs.values()

    def __init__(self, name):
        # type: (str) -> NoReturn
        self.__name = name
        self.__inputs = {}
        self.__outputs = {}
        self.__data = None

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def uninitialize(self):
        pass

    @abstractmethod
    def compute(self):
        pass

    def add_input_attribute(self, name):
        # type: (str) -> Attribute
        """add the input attribute"""
        attr = Attribute(name, self)
        self.__inputs[name] = attr
        return attr

    def add_output_attribute(self, name):
        # type: (str) -> Attribute
        """add the output attribute"""
        attr = Attribute(name, self)
        self.__outputs[name] = attr
        return attr

    def propagate(self):
        # type:() -> bool
        has_next = False
        for output in self.__outputs.values():
            has_next = has_next or output.propagate()
        return has_next


class ConstNode(Node):
    """Constant Node"""

    @property
    def output(self):
        # type: () -> Attribute
        return self.__output

    def __init__(self, data):
        # type: (object) -> NoReturn
        super(ConstNode, self).__init__('const')
        self.__output = None
        self.data = data

    def initialize(self):
        self.__output = self.add_output_attribute(self.__output)

    def uninitialize(self):
        pass

    def compute(self):
        self.__output.value = self.data


class AddNode(Node):
    """Arithmetic Addition Node"""

    @property
    def input1(self):
        # type: () -> Attribute
        return self.__input1

    @property
    def input2(self):
        # type: () -> Attribute
        return self.__input2

    @property
    def output(self):
        # type: () -> Attribute
        return self.__output

    def __init__(self):
        super(AddNode, self).__init__('add')
        self.__input1 = None
        self.__input2 = None
        self.__output = None

    def initialize(self):
        self.__input1 = self.add_input_attribute('input1')
        self.__input2 = self.add_input_attribute('input2')
        self.__output = self.add_output_attribute('output')

    def uninitialize(self):
        pass

    def compute(self):
        self.__output.value = self.__input1.value + self.__input2.value


if __name__ == '__main__':
    const1 = ConstNode(1)
    const1.initialize()

    const2 = ConstNode(2)
    const2.initialize()

    add1 = AddNode()
    add1.initialize()

    const1.output.connect(add1.input1)
    const2.output.connect(add1.input2)

    const1.compute()
    const1.propagate()

    const2.compute()
    const2.propagate()

    add1.compute()

    print '{} + {} = {}'.format(const1.data, const2.data, add1.output.value)


