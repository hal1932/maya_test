# coding: utf-8
import maya.api.OpenMaya as om2


class MayaObject(object):

    @property
    def apiobj(self): return self.__get_apiobj()

    def __init__(self, source):
        self.__apiobj = None

        if isinstance(source, om2.MObject):
            self.__apiobj = source
        elif isinstance(source, om2.MPlug):
            self.__apiobj = source
        elif hasattr(source, '__call__'):
            self.__apiobj_selector = source

    def has_fn(self, mfn):
        return self.apiobj.hasFn(mfn)

    def __get_apiobj(self):
        if self.__apiobj is None:
            self.__apiobj = self.__apiobj_selector()
        return self.__apiobj

