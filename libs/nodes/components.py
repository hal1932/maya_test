# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.api.OpenMaya as om2

from libs.nodes.nodetypes import DagNode


__all__ = ['Components']


class Components(object):

    @staticmethod
    def from_sequence(sequence, mfn_type, dimension):
        # type: (Union[List[int], List[List[int]]], int, int) -> Components
        comps = _create_mfn(dimension)
        comps.create(mfn_type)
        comps.addElements(sequence)

        instance = Components(comps.object())
        instance.__mfn = comps
        return instance

    @staticmethod
    def from_selection():
        # type: () -> Dict[DagNode, Components]
        result = {}
        sel = om2.MGlobal.getActiveSelectionList()
        for i in range(sel.length()):
            mdagpath, mobj = sel.getComponent(i)
            result[DagNode(mdagpath)] = Components(mobj)
        return result

    @property
    def mobject(self):
        # type: () -> om2.MObject
        return self.__mobj

    @property
    def mfn(self):
        # type: () -> Union[om2.MFnSingleIndexedComponent, om2.MFnDoubleIndexedComponent, om2.MFnTripleIndexedComponent]
        return self.__mfn

    @property
    def type(self):
        # type: () -> int
        return self.mfn.componentType

    @property
    def dimension(self):
        # type: () -> int
        if isinstance(self.mfn, om2.MFnSingleIndexedComponent):
            return 1
        if isinstance(self.mfn, om2.MFnDoubleIndexedComponent):
            return 2
        if isinstance(self.mfn, om2.MFnTripleIndexedComponent):
            return 3
        raise NotImplementedError(self.mfn.__class__)

    def __init__(self, source):
        # type: (Union[[str], om2.MObject, om2.MFnComponent]) -> NoReturn
        if isinstance(source, (list, set)):
            if len(source) == 0:
                raise ValueError('sources is empty')

            mfn_type_str = source[0].split('.')[-1].split('[')[0]
            mfn_type, dimension = _get_desc(mfn_type_str)

            indices = []
            for item in source:
                index_str = item.split('[')[-1].rstrip(']')
                if ':' in index_str:
                    start_str = index_str.split(':')[0]
                    end_str = index_str[len(start_str) + 1:]
                    for i in range(int(start_str), int(end_str) + 1):
                        indices.append(i)
                else:
                    indices.append(int(index_str))

            comps = _create_mfn(dimension)
            comps.create(mfn_type)
            comps.addElements(indices)

            self.__mobj = comps.object()
            self.__mfn = comps

        elif isinstance(source, om2.MObject):
            if source.hasFn(om2.MFn.kSingleIndexedComponent):
                dimension = 1
            elif source.hasFn(om2.MFn.kDoubleIndexedComponent):
                dimension = 2
            elif source.hasFn(om2.MFn.kTripleIndexedComponent):
                dimension = 3
            else:
                raise ValueError(source)

            comps = _create_mfn(dimension)
            comps.create(source.apiType())
            comps.setObject(source)

            self.__mobj = source
            self.__mfn = comps

        elif isinstance(source, om2.MFnComponent):
            self.__mobj = source.object()
            self.__mfn = source

        else:
            raise ValueError(source)

        self.__current_index = 0

    def __repr__(self):
        return '{} {} {}'.format(self.__class__, self.type, list(self.mfn.getElements()))

    def append(self, item):
        # type: (Union[[int], List[List[int]]]) -> NoReturn
        self.mfn.addElement(item)

    def extend(self, items):
        # type: ([Union[[int], [[int,int]], [[int,int,int]]]]) -> NoReturn
        self.mfn.addElements(items)

    def elements(self):
        # type: () -> om2.MIntArray
        return self.mfn.getElements()

    def __len__(self):
        return self.mfn.elementCount

    def __getitem__(self, item):
        return self.mfn.element(item)

    def __iter__(self):
        self.__current_index = 0
        return self

    def __next__(self):
        if self.__current_index >= len(self):
            raise StopIteration()

        item = self[self.__current_index]
        self.__current_index += 1
        return item

    def next(self):
        return self.__next__()


def _get_desc(type_str):
    # type: (str) -> Tuple(int, int)
    if type_str == 'vtx': return om2.MFn.kMeshVertComponent, 1
    if type_str == 'f': return om2.MFn.kMeshPolygonComponent, 1
    if type_str == 'e': return om2.MFn.kMeshEdgeComponent, 1
    if type_str == 'map': return om2.MFn.kMeshMapComponent, 1
    if type_str == 'faceVtx': return om2.MFn.kMeshFaceVertComponent, 1
    if type_str == 'vtxFace': return om2.MFn.kMeshVtxFaceComponent, 1
    raise NotImplementedError('type: {}'.format(type_str))


def _create_mfn(dimension):
    # type: (int) -> Union[om2.MFnSingleIndexedComponent, om2.MFnDoubleArrayData, om2.MFnTripleIndexedComponent]
    if dimension == 1: return om2.MFnSingleIndexedComponent()
    if dimension == 2: return om2.MFnDoubleIndexedComponent()
    if dimension == 3: return om2.MFnTripleIndexedComponent()
    raise NotImplementedError('dimension: {}'.format(dimension))
