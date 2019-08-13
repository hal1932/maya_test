# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

from libs.gui.pyside_modules import *

try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

import maya.OpenMayaUI as omui


class MayaMainWindowBase(QMainWindow, MayaQWidgetBaseMixin):

    @staticmethod
    def get_maya_window():
        # type: () -> QWidget
        maya_main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(maya_main_window_ptr), QWidget)

    @property
    def class_name(self):
        # type: () -> NoReturn
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

    def __init__(self):
        maya_window = MayaMainWindowBase.get_maya_window()

        for child in maya_window.children():
            # reload でポインタが変わったときのために名前で比較する
            if child.objectName() == self.class_name:
                child.close()

        super(MayaMainWindowBase, self).__init__(parent=maya_window)
        self.setObjectName(self.class_name)

    def setup_ui(self):
        # type: () -> MayaMainWindowBase
        widget = self.centralWidget()
        if widget is not None:
            widget.deleteLater()
        widget = QWidget()

        self.setCentralWidget(widget)
        self._setup_ui(widget)
        return self

    def closeEvent(self, _):
        # type: (QCloseEvent) -> NoReturn
        self._shutdown_ui()

    def _setup_ui(self, central_widget):
        # type: (QWidget) -> NoReturn
        pass

    def _shutdown_ui(self):
        pass


class MayaAppBase(object):

    def __init__(self):
        self._window = None

    def execute(self):
        app = QApplication.instance()
        self._initialize(app)
        self._window = self._create_window()
        if self._window is not None:
            self._window.setup_ui().show()

    def _initialize(self, app):
        # type: (QApplication) -> nore
        pass

    def _create_window(self):
        # type: () -> MayaMainWindowBase
        pass

