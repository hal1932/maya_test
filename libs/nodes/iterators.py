# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.api.OpenMaya as om2

__all__ = ['VertexIter', 'FaceIter', 'FaceVertexIter', 'EdgeIter']


class Iterator(object):

    @property
    def index(self):
        # type: () -> int
        return self._iter.index()

    @property
    def current_item(self):
        # type: () -> om2.MObject
        return self._iter.currentItem()

    def __init__(self, iter):
        self._iter = iter
        self._first_iteration = True

    def __iter__(self):
        self._first_iteration = True
        return self

    def __next__(self):
        if self._first_iteration:
            self._first_iteration = False
            return self

        self._iter.next()

        if self._iter.isDone():
            raise StopIteration()

        return self

    def next(self):
        return self.__next__()


class VertexIter(Iterator):

    @property
    def position(self):
        # type: () -> om2.MPoint
        return self._iter.position()

    @property
    def uv_count(self):
        # type: () -> int
        return self._iter.numUVs()

    @property
    def uv(self):
        # type: () -> [float, float]
        return self._iter.getUV()

    @property
    def uv_indices(self):
        # type: () -> om2.MIntArray
        return self._iter.getUVIndices()

    @property
    def has_color(self):
        # type: () -> bool
        return self._iter.hasColor()

    @property
    def color(self):
        # type: () -> om2.MColor
        return self._iter.getColor()

    @property
    def normal(self):
        # type: () -> om2.MVector
        return self._iter.getNormal()

    @property
    def normals(self):
        # type: () -> om2.MVectorArray
        return self._iter.getNormals()

    @property
    def on_boundary(self):
        # type: () -> bool
        return self._iter.onBoundary()

    @property
    def connected_edges(self):
        # type: () -> om2.MIntArray
        return self._iter.getConnectedEdges()

    @property
    def connected_faces(self):
        # type: () -> om2.MIntArray
        return self._iter.getConnectedFaces()

    @property
    def connected_vertices(self):
        # type: () -> om2.MIntArray
        return self._iter.getConnectedVertices()

    def __init__(self, iter):
        # type: (om2.MItMeshVertex) -> NoReturn
        super(VertexIter, self).__init__(iter)

    def get_position(self, space):
        # type: (om2.MSpace) -> om2.MPoint
        return self._iter.position(space)

    def get_uv(self, uv_set):
        # type: (str) -> List[float]
        return self._iter.getUV(uv_set)

    def get_uv_indices(self, uv_set):
        # type: (str) -> om2.MIntArray
        return self._iter.getUVIndices(uv_set)

    def get_uvs(self, uv_set):
        # type: (str) -> [om2.MFloatArray, om2.MFloatArray, om2.MIntArray]
        return self._iter.getUVs(uv_set)

    def get_color(self, color_set):
        # type: (str) -> om2.MColor
        return self._iter.getColor(color_set)

    def get_normal(self, space):
        # type: (om2.MSpace) -> om2.MVector
        return self._iter.getNormal(space)

    def get_normals(self, space):
        # type: (om2.MSpace) -> om2.MVectorArray
        return self._iter.getNormals(space)


class FaceIter(Iterator):

    @property
    def center(self):
        # type: () -> om2.MPoint
        return self._iter.center()

    @property
    def area(self):
        # type: () -> float
        return self._iter.getArea()

    @property
    def normal(self):
        # type: () -> om2.MVector
        return self._iter.getNormal()

    @property
    def vertices(self):
        # type: () -> om2.MIntArray
        return self._iter.getVertices()

    @property
    def vertex_count(self):
        # type: () -> int
        return self._iter.polygonVertexCount()

    @property
    def edges(self):
        # type: () -> om2.MIntArray
        return self._iter.getEdges()

    @property
    def connected_vertices(self):
        # type: () -> om2.MIntArray
        return self._iter.getConnectedVertices()

    @property
    def connected_faces(self):
        # type: () -> om2.MIntArray
        return self._iter.getConnectedFaces()

    @property
    def connected_edges(self):
        # type: () -> om2.MIntArray
        return self._iter.getConnectedEdges()

    @property
    def uv_indices(self):
        # type() -> [int]
        return [self._iter.getUVIndex(x) for x in range(self._iter.polygonVertexCount())]

    def __init__(self, iter):
        # type: (om2.MItMeshPolygon) -> NoReturn
        super(FaceIter, self).__init__(iter)

    # Maya 2016.5 のバグ回避用に個別実装
    def __next__(self):
        if self._first_iteration:
            self._first_iteration = False
            return self

        self._iter.next(self._iter) # 引数に self._iter を渡さないとバグる

        if self._iter.isDone():
            raise StopIteration()

        return self

    def get_center(self, space):
        # type: (om2.MSpace) -> om2.MPoint
        return self._iter.center(space)

    def get_normal(self, space):
        # type: (om2.MSpace) -> om2.MVector
        return self._iter.getNormal(space)


class FaceVertexIter(Iterator):

    @property
    def index(self):
        # type: () -> int
        return self._iter.faceVertexId()

    @property
    def face(self):
        # type: () -> int
        return self._iter.faceId()

    @property
    def vertex(self):
        # type: () -> int
        self._iter.vertexId()

    @property
    def color(self):
        # type: () -> om2.MColor
        return self._iter.getColor()

    @property
    def position(self):
        # type: () -> om2.MPoint
        return self._iter.position()

    @property
    def normal(self):
        # type: () -> om2.MVector
        return self._iter.getNormal()

    @property
    def tangent(self):
        # type: () -> om2.MVector
        return self._iter.getTangent()

    @property
    def binormal(self):
        # type: () -> om2.MVector
        return self._iter.getBinormal()

    def __init__(self, iter):
        # type: (om2.MItMeshFaceVertex) -> NoReturn
        super(FaceVertexIter, self).__init__(iter)

    def get_color(self, color_set):
        # type: (str) -> om2.MColor
        return self._iter.getColor(color_set)

    def get_position(self, space):
        # type: (om2.MSpace) -> om2.MPoint
        return self._iter.position(space)

    def get_normal(self, space):
        # type: (om2.MSpace) -> om2.MVector
        return self._iter.getNormal(space)

    def get_tangent(self, space):
        # type: (om2.MSpace) -> om2.MVector
        return self._iter.getTangent(space)

    def get_binormal(self, space):
        # type: (om2.MSpace) -> om2.MVector
        return self._iter.getBinormal(space)


class EdgeIter(Iterator):

    @property
    def center(self):
        # type: () -> om2.MPoint
        return self._iter.center()

    @property
    def length(self):
        # type: () -> float
        return self._iter.length()

    @property
    def vertices(self):
        # type: () -> [om2.MPoint, om2.MPoint]
        return [self._iter.vertexId(0), self._iter.vertexId(1)]

    @property
    def connected_edges(self):
        # type: () -> om2.MIntArray
        return self._iter.getConnectedEdges()

    @property
    def connected_faces(self):
        # type: () -> om2.MIntArray
        return self._iter.getConnectedFaces()

    def __init__(self, iter):
        # type: (om2.MItMeshEdge) -> NoReturn
        super(EdgeIter, self).__init__(iter)

    def get_center(self, space):
        # type: (om2.MSpace) -> om2.MPoint
        return self._iter.center(space)

    def get_length(self, space):
        # type: (om2.MSpace) -> float
        return self._iter.length(space)
