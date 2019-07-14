# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import functools

import maya.api.OpenMaya as om2
import maya.cmds as cmds

from libs.nodes.general import MayaObject
from libs.nodes.attribute import Attribute
from libs.nodes.iterators import *


def _get_depend_node_obj(name):
    # type: (str) -> om2.MObject
    try:
        sel_list = om2.MGlobal.getSelectionListByName(name)
        return sel_list.getDependNode(0)
    except RuntimeError:
        raise NameError(name)


def _get_dagpath_obj(name):
    # type: (str) -> om2.MDagPath
    try:
        sel_list = om2.MGlobal.getSelectionListByName(name)
        return sel_list.getDagPath(0)
    except RuntimeError:
        raise NameError(name)


def _ls(cls, *args, **kwargs):
    # type: (str) -> List[cls]
    return [cls(name) for name in cmds.ls(*args, **kwargs)]


class DependNode(MayaObject):

    _mfn_type = om2.MFnDependencyNode
    _node_type = om2.MFn.kDependencyNode

    @staticmethod
    def ls(*args, **kwargs):
        # type: (*args, **kwargs) -> List[DependNode]
        kwargs['dependencyNodes'] = True
        return _ls(DependNode, *args, **kwargs)

    @property
    def name(self):
        # type: () -> str
        return self.mfn.name()

    @property
    def fullname(self):
        # type: () -> str
        return self.mfn.absoluteName()

    @property
    def mobject(self):
        # type: () -> om2.MObject
        return self.apiobj

    @property
    def mfn(self):
        # type: () -> _mfn_type
        return self.__get_mfn()

    def __init__(self, source):
        # type: (Union[str, om2.MObject, Callable[[], om2.MObject]]) -> NoReturn
        if isinstance(source, (str, unicode)):
            source = functools.partial(_get_depend_node_obj, source)
        super(DependNode, self).__init__(source)

        self.__mfn = None
        self.__attributes = {}

    def __getattr__(self, item):
        # type: (str) -> Attribute
        attribute = self.__attributes.get(item, None)
        if attribute is not None:
            return attribute

        plug = self.mfn.findPlug(item, False)
        if plug is None:
            return AttributeError(item)

        attribute = Attribute(plug)
        self.__attributes[item] = attribute

        return attribute

    def __repr__(self):
        return '{} {}'.format(self.__class__, self.name)

    def __get_mfn(self):
        if self.__mfn is None:
            mobj = self.mobject
            self.__mfn = self.__class__._mfn_type(mobj)
        return self.__mfn


class DagNode(DependNode):

    _mfn_type = om2.MFnDagNode
    _node_type = om2.MFn.kDagNode

    @staticmethod
    def ls(*args, **kwargs):
        # type: (*args, **kwargs) -> List[DagNode]
        kwargs['dagObjects'] = True
        return _ls(DagNode, *args, **kwargs)

    @property
    def mdagpath(self):
        # type: () -> om2.MDagPath
        return self.__get_mdagpath_obj()

    @property
    def child_count(self):
        # type: () -> int
        return self.mfn.childCount()

    def __init__(self, source):
        # type: (Union[str, om2.MDagPath, om2.MObject, Callable[[], om2.MObject]]) -> NoReturn
        if isinstance(source, om2.MDagPath):
            self.__mdagpath = source
            source = self.__mdagpath.node()
        else:
            self.__mdagpath = None

        super(DagNode, self).__init__(source)

    def children(self, cls=None):
        # type: (type) -> Iterable[cls]
        if cls is None:
            cls = DagNode
        for i in range(self.child_count):
            child_obj = self.mfn.child(i)
            yield cls(child_obj)

    def __get_mdagpath_obj(self):
        if self.__mdagpath is None:
            self.__mdagpath = _get_dagpath_obj(self.name)
        return self.__mdagpath


class Transform(DagNode):

    _mfn_type = om2.MFnTransform
    _node_type = om2.MFn.kTransform

    @staticmethod
    def ls(*args, **kwargs):
        # type: (*args, **kwargs) -> List[Transform]
        kwargs['type'] = 'transform'
        return _ls(Transform, *args, **kwargs)

    def __init__(self, source):
        # type: (Union[str, om2.MObject, Callable[[], om2.MObject]]) -> NoReturn
        super(Transform, self).__init__(source)

    def shape(self):
        # type: () -> Iterable[Shape]
        shape_obj = self.mdagpath.extendToShape()
        return Shape(shape_obj)


class Shape(DagNode):

    _node_type = om2.MFn.kShape

    @staticmethod
    def ls(*args, **kwargs):
        # type: (*args, **kwargs) -> List[Shape]
        kwargs['shapes'] = True
        return _ls(Shape, *args, **kwargs)

    def __init__(self, source):
        # type: (Union[str, om2.MObject, Callable[[], om2.MObject]]) -> NoReturn
        super(Shape, self).__init__(source)


class Mesh(Shape):

    _mfn_type = om2.MFnMesh
    _node_type = om2.MFn.kMesh

    @staticmethod
    def ls(*args, **kwargs):
        # type: (*args, **kwargs) -> List[Mesh]
        kwargs['type'] = 'mesh'
        return _ls(Mesh, *args, **kwargs)

    def __init__(self, source):
        # type: (Union[str, om2.MObject, Callable[[], om2.MObject]]) -> NoReturn
        super(Mesh, self).__init__(source)

    def vertices(self, comps=None):
        # type: (Components) -> VertexIter
        if comps is None:
            iter = om2.MItMeshVertex(self.mobject)
        else:
            iter = om2.MItMeshVertex(self.mdagpath, comps.mobject)
        return VertexIter(iter)

    def faces(self, comps=None):
        # type: (Components) -> FaceIter
        if comps is None:
            iter = om2.MItMeshPolygon(self.mobject)
        else:
            iter = om2.MItMeshPolygon(self.mdagpath, comps.mobject)
        return FaceIter(iter)

    def face_vertices(self, comps=None):
        # type: (Components) -> FaceVertexIter
        if comps is None:
            iter = om2.MItMeshFaceVertex(self.mobject)
        else:
            iter = om2.MItMeshFaceVertex(self.mdagpath, comps.mobject)
        return FaceVertexIter(iter)

    def edges(self, comps=None):
        # type: (Components) -> EdgeIter
        if comps is None:
            iter = om2.MItMeshEdge(self.mobject)
        else:
            iter = om2.MItMeshEdge(self.mdagpath, comps.mobject)
        return EdgeIter(iter)












