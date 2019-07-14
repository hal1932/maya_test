# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

from tools.node_editor.nodes.node import *


class NodeGraph(object):

    def __init__(self):
        self.__nodes = []

    def add_node(self, node):
        # type: (Node) -> NoReturn
        self.__nodes.append(node)

    def evaluate(self, node):
        # type: (Node) -> NoReturn
        traversals = [[node]]

        nodes = [node]
        while len(nodes) > 0:
            node = nodes.pop()
            parents = []
            for input in node.inputs:
                parents.append(input.source.node)
            nodes.extend(parents)
            traversals.append(parents)

        for nodes in reversed(traversals):
            for node in nodes:
                node.compute()
                node.propagate()


if __name__ == '__main__':
    const1 = ConstNode(1)
    const1.initialize()

    const2 = ConstNode(2)
    const2.initialize()

    const3 = ConstNode(3)
    const3.initialize()

    add1 = AddNode()
    add1.initialize()

    add2 = AddNode()
    add2.initialize()

    const1.output.connect(add1.input1)
    const2.output.connect(add1.input2)

    add1.output.connect(add2.input1)
    const3.output.connect(add2.input2)

    graph = NodeGraph()
    graph.add_node(const1)
    graph.add_node(const2)
    graph.add_node(const3)
    graph.add_node(add1)
    graph.add_node(add2)

    graph.evaluate(add2)

    print '{} + {} = {}'.format(const1.data, const2.data, add1.output.value)
    print '({} + {}) + {} = {}'.format(const1.data, const2.data, const3.data, add2.output.value)
