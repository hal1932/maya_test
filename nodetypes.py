# coding : utf-8
import functools
import maya.api.OpenMaya as om2

from general import MayaObject
from attribute import Attribute


def _get_depend_node_obj(name):
    sel_list = om2.MGlobal.getSelectionListByName(name)
    return sel_list.getDependNode(0)


class DependNode(MayaObject):

    _mfn_type = om2.MFnDependencyNode
    _node_type = om2.MFn.kDependencyNode

    @property
    def name(self): return self.mfn.name()

    @property
    def mobject(self): return self.apiobj

    @property
    def mfn(self): return self.__get_mfn()

    def __init__(self, source):
        if isinstance(source, (str, unicode)):
            source = functools.partial(_get_depend_node_obj, source)

        super(self.__class__, self).__init__(source)

        self.__mfn = None
        self.__attributes = {}

    def __getattr__(self, item):
        attribute = self.__attributes.get(item, None)
        if attribute is not None:
            return attribute

        plug = self.mfn.findPlug(item, False)
        if plug is None:
            return AttributeError(item)

        attribute = Attribute(plug)
        self.__attributes[item] = attribute

        return attribute

    def __get_mfn(self):
        if self.__mfn is None:
            mobj = self.mobject
            self.__mfn = self.__class__._mfn_type(mobj)
        return self.__mfn
