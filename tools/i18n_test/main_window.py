# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import os

from libs.gui.pyside_modules import *
from libs.gui.layouts import *
from libs.gui.maya import *


class MainWindow(MayaMainWindowBase):

    lang_switch_requested = Signal(str)

    def __init__(self):
        super(MainWindow, self).__init__()

    def _setup_ui(self, central_widget):
        # type: (QWidget) -> NoReturn
        self.setWindowTitle(self.tr('window_title'))

        def switch_lang(name):
            self.lang_switch_requested.emit(name)
            self.setup_ui()

        lang_switch_jajp = QPushButton(self.tr('lang_jajp'))
        lang_switch_jajp.clicked.connect(lambda: switch_lang('ja_JP'))

        lang_switch_enus = QPushButton(self.tr('lang_enus'))
        lang_switch_enus.clicked.connect(lambda: switch_lang('en_US'))

        central_widget.setLayout(vbox(
            hbox(
                lang_switch_jajp,
                lang_switch_enus,
            ),
            QLabel(self.tr('label1')),
            QLabel(self.tr('label2')),
        ))


class MayaApp(MayaAppBase):

    def __init__(self):
        super(MayaApp, self).__init__()
        self.__translator = QTranslator()

    def _initialize(self, app):
        # type: (QApplication) -> NoReturn
        self.__switch_languages('ja_JP')
        app.installTranslator(self.__translator)

    def _create_window(self):
        # type: () -> MayaMainWindowBase
        window = MainWindow()
        window.lang_switch_requested.connect(lambda lang: self.__switch_languages(lang))
        return window

    def __switch_languages(self, lang_name):
        # type: (str) -> NoReturn
        self.__translator.load(lang_name, directory=os.path.join(os.path.dirname(__file__), 'i18n'))


def main():
    app = MayaApp()
    app.execute()
