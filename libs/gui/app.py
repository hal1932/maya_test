# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import sys

from libs.gui.pyside_modules import *


class MainWindowBase(QMainWindow):

    @property
    def absolute_name(self):
        # type: () -> str
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

    def __init__(self, parent=None, enable_multiple_activation=False):
        # type: (QWidget, bool) -> NoReturn
        if not enable_multiple_activation:
            self._prevent_multiple_activation()
        super(MainWindowBase, self).__init__(parent)
        self.setObjectName(self.absolute_name)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def setup_ui(self):
        # type: () -> MainWindowBase
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

    def _prevent_multiple_activation(self):
        # type: () -> NoReturn
        for children in QApplication.instance().findChildren(QMainWindow):
            print(children)

    def _setup_ui(self, central_widget):
        # type: (QWidget) -> NoReturn
        pass

    def _shutdown_ui(self):
        pass


class AppBase(object):

    def __init__(self):
        self._window = None

    def execute(self):
        self._execute()
        sys.exit(app.exec_())

    def execute(self):
        app = self._setup_application()

        self._initialize(app)
        self._window = self._create_window()
        if self._window is not None:
            self._window.setup_ui().show()

        self._exec_application_main_loop(app)

    def _setup_application(self):
        # type: () -> QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        return app

    def _exec_application_main_loop(self, app):
        # type: (QApplication) -> NoReturn
        sys.exit(app.exec_())

    def _initialize(self, app):
        # type: (QApplication) -> nore
        pass

    def _create_window(self):
        # type: () -> MainWindowBase
        pass


if __name__ == '__main__':
    class MyMainWindow(MainWindowBase):
        def __init__(self):
            super(MyMainWindow, self).__init__()

        def _setup_ui(self, central_widget):
            # type: (QWidget) -> NoReturn
            self.setWindowTitle('window title')

        def _shutdown_ui(self):
            print('shotdown {}'.format(self.winId()))

    class MyApp(AppBase):
        def __init__(self):
            super(MyApp, self).__init__()

        def _create_window(self):
            # type: () -> MainWindowBase
            return MyMainWindow()

    app = MyApp()
    app.execute()
