# coding: utf-8
import maya.api.OpenMaya as om2

from nodes.general import MayaObject


# alternative to six.moves
range = xrange


class Attribute(MayaObject):

    @property
    def name(self): return self.mplug.name()

    @property
    def mobject(self): return self.apiobj

    @property
    def mplug(self): return self.__mplug

    def __init__(self, mplug):
        super(self.__class__, self).__init__(mplug.attribute())
        self.__mplug = mplug

    def __getitem__(self, item):
        if not self.mplug.isArray:
            raise RuntimeError('{} is not array'.format(self.name))
        if item >= self.mplug.numElements():
            raise IndexError('index {}[{}] out of bounds {}'.format(self.name, item, self.mplug.numElements()))
        return Attribute(self.mplug.elementByLogicalIndex(item))

    def get(self):
        if self.mplug.isNull:
            return None
        if self.mplug.isNetworked:
            raise RuntimeError('{} is networked'.format(self.name))
        return _getattr_impl(self.mplug)


def _getattr_impl(mplug):
    mobj = mplug.attribute()
    api_type = mobj.apiType()

    # array
    if mplug.isArray:
        return [_getattr_impl(mplug.elementByLogicalIndex(i)) for i in range(mplug.numElements())]

    # compound
    if mplug.isCompound:
        # if om2.MFn.kAttribute2Double <= api_type <= om2.MFn.kAttribute4Double:
        #     return mplug.asMDataHandle().asVector()
        return [_getattr_impl(mplug.child(i)) for i in range(mplug.numChildren())]

    # typed
    if api_type == om2.MFn.kTypedAttribute:
        attr_type = om2.MFnTypedAttribute(mobj).attrType()
        return _typed_attr_table[attr_type](mplug)

    # numeric
    if api_type == om2.MFn.kNumericAttribute:
        numeric_type = om2.MFnNumericAttribute(mobj).numericType()
        return _numeric_attr_table[numeric_type](mplug)

    return _api_type_table[api_type](mplug)


_api_type_table = {
    om2.MFn.kDoubleLinearAttribute: lambda plug: plug.asDouble(),
    om2.MFn.kFloatLinearAttribute: lambda plug: plug.asFloat(),
    om2.MFn.kDoubleAngleAttribute: lambda plug: plug.asMAngle().asDegrees(),
    om2.MFn.kFloatAngleAttribute: lambda plug: plug.asMAngle().asDegrees(),
    om2.MFn.kEnumAttribute: lambda plug: plug.asInt(),
    om2.MFn.kMatrixAttribute: lambda plug: om2.MFnMatrixAttribute(plug.asMObject()).matrix(),
}

_typed_attr_table = {
    om2.MFnData.kString: lambda plug: plug.asString(),
    om2.MFnData.kMatrix: lambda plug: om2.MFnMatrixData(plug.asMObject()).matrix(),
}

_numeric_attr_table = {
    om2.MFnNumericData.kBoolean: lambda plug: plug.asBool(),
    om2.MFnNumericData.kInt: lambda plug: plug.asInt(),
    om2.MFnNumericData.kByte: lambda plug: plug.asInt(),
    om2.MFnNumericData.kShort: lambda plug: plug.asInt(),
    om2.MFnNumericData.kLong: lambda plug: plug.asInt(),
    om2.MFnNumericData.kDouble: lambda plug: plug.asDouble(),
    om2.MFnNumericData.kFloat: lambda plug: plug.asDouble(),
    om2.MFnNumericData.kAddr: lambda plug: plug.asDouble(),
}
