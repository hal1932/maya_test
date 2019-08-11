# coding: utf-8
from __future__ import absolute_import
from typing import *
from six import add_metaclass
from six.moves import *

from abc import ABCMeta, abstractmethod

from tools.node_editor.nodes.attribute import Attribute


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
        if value == self.__data:
            return

        self.__data = value
        for output in self.outputs:
            output.set_dirty()

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

    def evaluate(self):
        # type: () -> NoReturn
        for input in self.inputs:
            input.evaluate()

        self.compute()

        for output in self.outputs:
            output.send_value()

    def _set_attribute_affect(self, source, dest):
        # type: (Attribute, Attribute) -> NoReturn
        source._set_affect(dest)


class ConstNode(Node):
    """Constant Node"""

    @property
    def output(self):
        # type: () -> Attribute
        return self.__output

    def __init__(self, name, data=None):
        # type: (str, object) -> NoReturn
        super(ConstNode, self).__init__(name)
        self.__output = None
        self.set_data(data)

    def set_data(self, data):
        # type: (object) -> NoReturn
        self.data = data

    def initialize(self):
        self.__output = self.add_output_attribute('output')

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

    def __init__(self, name):
        # type: (str) -> NoReturn
        super(AddNode, self).__init__(name)
        self.__input1 = None
        self.__input2 = None
        self.__output = None

    def initialize(self):
        self.__input1 = self.add_input_attribute('input1')
        self.__input2 = self.add_input_attribute('input2')
        self.__output = self.add_output_attribute('output')
        self._set_attribute_affect(self.__input1, self.__output)
        self._set_attribute_affect(self.__input2, self.__output)

    def uninitialize(self):
        pass

    def compute(self):
        if self.__input1.value is None or self.__input2.value is None:
            return
        self.__output.value = self.__input1.value + self.__input2.value

