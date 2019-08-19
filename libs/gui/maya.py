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

from libs.gui.app import MainWindowBase, AppBase


class MayaMainWindowBase(MainWindowBase, MayaQWidgetBaseMixin):

    @staticmethod
    def get_maya_window():
        # type: () -> QWidget
        maya_main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(maya_main_window_ptr), QWidget)

    def __init__(self):
        maya_window = MayaMainWindowBase.get_maya_window()
        super(MayaMainWindowBase, self).__init__(parent=maya_window, enable_multiple_activation=False)

    def _prevent_multiple_activation(self):
        maya_window = MayaMainWindowBase.get_maya_window()
        for child in maya_window.children():
            # reload でポインタが変わったときのために名前で比較する
            if child.objectName() == self.absolute_name:
                child.close()


class MayaAppBase(AppBase):

    def __init__(self):
        super(MayaAppBase, self).__init__()

    def _setup_application(self):
        # type: () -> QApplication
        return QApplication.instance()

    def _exec_application_main_loop(self, app):
        # type: (QApplication) -> NoReturn
        pass


if __name__ == '__main__':
    class MyMainWindow(MayaMainWindowBase):
        def __init__(self):
            super(MyMainWindow, self).__init__()

        def _setup_ui(self, central_widget):
            # type: (QWidget) -> NoReturn
            self.setWindowTitle('window title')

        def _shutdown_ui(self):
            print('shotdown {}'.format(self.winId()))

    class MyApp(MayaAppBase):
        def __init__(self):
            super(MyApp, self).__init__()

        def _create_window(self):
            # type: () -> MainWindowBase
            return MyMainWindow()

    app = MyApp()
    app.execute()
