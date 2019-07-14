# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.api.OpenMaya as om2
import maya.cmds as cmds


class MayaObject(object):

    @property
    def apiobj(self):
        # type: () -> Union[om2.MObject, om2.MPlug]
        return self.__get_apiobj()

    def __init__(self, source):
        # type: (Union[om2.MObject, om2.MPlug, Callable[[], om2.MObject]]) -> NoReturn
        self.__apiobj = None

        if isinstance(source, MayaObject):
            self.__apiobj = source.apiobj
        elif isinstance(source, om2.MObject):
            self.__apiobj = source
        elif isinstance(source, om2.MPlug):
            self.__apiobj = source
        elif hasattr(source, '__call__'):
            self.__apiobj_selector = source

    def __repr__(self):
        return '{} {}'.format(self.__class__, self.apiobj)

    def has_fn(self, mfn_type):
        # type: (om2.MFn) -> bool
        return self.apiobj.hasFn(mfn_type)

    def __get_apiobj(self):
        # type: () -> Union[om2.MObject, om2.MPlug]
        if self.__apiobj is None:
            self.__apiobj = self.__apiobj_selector()
        return self.__apiobj

