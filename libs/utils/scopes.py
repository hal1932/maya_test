# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.cmds as cmds


def undo_scope(func):
    def _wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        func(*args, **kwargs)
        cmds.undoInfo(closeChunk=True)
    return _wrapper


def keep_selection_scope(func):
    def _wrapper(*args, **kwargs):
        selection = cmds.ls(sl=True)
        func(*args, **kwargs)
        cmds.select(selection, replace=True)
    return _wrapper

