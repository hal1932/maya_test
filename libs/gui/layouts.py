# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

from gui.pyside_modules import *


def hbox(*items):
    # type: (List[Union[QWidget, QLayout, str]]) -> QHBoxLayout
    return _box(QHBoxLayout, items)


def vbox(*items):
    # type: (List[Union[QWidget, QLayout, str]]) -> QVBoxLayout
    return _box(QVBoxLayout, items)


def stretch():
    # type: () -> str
    return 'stretch'


def _box(cls, items):
    # type: (type, List[Union[QWidget, QLayout, str]]) -> QBoxLayout
    layout = cls()

    for item in items:
        if isinstance(item, QWidget):
            layout.addWidget(item)
        elif isinstance(item, QLayout):
            layout.addLayout(item)
        elif isinstance(item, str):
            if item == stretch():
                layout.addStretch()

    return layout

