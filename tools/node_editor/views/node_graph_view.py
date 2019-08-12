# coding: utf-8
from __future__ import absolute_import
from typing import *

import inspect

from gui.pyside_modules import *
from gui.layouts import *
from gui.widgets import *

from tools.node_editor.views.node_view import NodeView
from tools.node_editor.views.graphics_view import GraphicsView
import tools.node_editor.nodes.node as node


class NodeGraphWidget(GraphicsView):

    def __init__(self, parent=None):
        super(NodeGraphWidget, self).__init__(parent)
        self.__scene = _NodeGraphScene()

        self.setScene(self.__scene)

        self.mouse_move.connect(self.on_mouse_move)
        self.mouse_wheel.connect(self.on_mouse_wheel)

    def setBackgroundBrush(self, brush):
        # type: (QBrush) -> NoReturn
        self.__scene.setBackgroundBrush(brush)

    def set_rect(self, rect):
        # type: (QRect) -> NoReturn
        self.__scene.setSceneRect(QRectF(rect))

    def add_node(self, cls, name):
        # type: (type, str) -> NodeView
        return self.__scene.add_node(cls, name)

    def on_mouse_wheel(self, wheel):
        # type: (MouseWheelEventArgs) -> NoReturn

        # Alt + Wheel -> ズーム
        if self.is_alt_key_pressed:
            transform = self.transform()
            if wheel.delta > 0:
                transform.scale(1.01, 1.01)
            else:
                transform.scale(0.99, 0.99)
            self.setTransform(transform)

            wheel.handled = True

    def on_mouse_move(self, move):
        # type: (MouseMoveEventArgs) -> NoReturn
        if self.is_alt_key_pressed:
            transform = self.transform()

            # Alt + 右ドラッグ → ズーム
            if move.buttons() == Qt.RightButton:
                self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
                delta_x = move.delta_pos.x()
                scale = 1.0 + delta_x * 0.001
                transform.scale(scale, scale)

            # Alt + 中ドラッグ → 移動
            elif move.buttons() == Qt.MiddleButton:
                self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                delta_x = move.delta_pos.x()
                delta_y = move.delta_pos.y()
                transform.translate(-delta_x, -delta_y)

            self.setTransform(transform)

            move.handled = True


class _NodeGraphScene(QGraphicsScene):

    def __init__(self, *args, **kwargs):
        super(_NodeGraphScene, self).__init__(*args, **kwargs)
        self.__mouse_overed_items = set()

    def add_node(self, cls, name):
        # type: (type, str) -> NodeItem
        model = cls(name)
        model.initialize()
        new_node = NodeView(self, name, model)
        self.update()
        return new_node

    def contextMenuEvent(self, e):
        # type: (QGraphicsSceneContextMenuEvent) -> NoReturn
        item = self.itemAt(e.scenePos(), QTransform())
        if item is not None:
            super(_NodeGraphScene, self).contextMenuEvent(e)
            return

        node_menus = {}
        for cls in node.__dict__.values():
            if not isinstance(cls, type) or not issubclass(cls, node.Node):
                continue
            if inspect.isabstract(cls):
                continue
            if not hasattr(cls, 'category'):
                continue

            category = cls.category()
            if category not in node_menus:
                node_menus[category] = []

            node_menus[category].append(cls)

        menu = QMenu()
        for category, items in node_menus.items():
            if category is None:
                for cls in items:
                    act = menu.addAction(cls.__name__)
                    act.node_cls = cls
            else:
                child = QMenu(category)
                for cls in items:
                    act = child.addAction(cls.__name__)
                    act.node_cls = cls
                menu.addMenu(child)

        action = menu.exec_(e.screenPos())
        if action is None:
            return

        node_cls = action.node_cls

        new_node = self.add_node(node_cls, node_cls.__name__)
        new_node.set_position(e.scenePos())

    def mouseMoveEvent(self, e):
        # type: (QGraphicsSceneMouseEvent) -> NoReturn

        # mouseOverEvent/mouseLeaveEventのカスタム実装
        all_items = self.items()
        over_items = self.items(e.scenePos())

        for item in all_items:
            if item in over_items:
                if hasattr(item, 'mouseOverEvent'):
                    item.mouseOverEvent(e)
                self.__mouse_overed_items.add(item)

            elif item in self.__mouse_overed_items:
                if hasattr(item, 'mouseLeaveEvent'):
                    item.mouseLeaveEvent(e)
                self.__mouse_overed_items.remove(item)

        super(_NodeGraphScene, self).mouseMoveEvent(e)


if __name__ == '__main__':
    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            view = NodeGraphWidget()
            view.setBackgroundBrush(QBrush(Qt.white))
            view.set_rect(QRect(0, 0, 640, 480))

            node1 = view.add_node(node.ConstNode, 'node1')
            node1.set_position(QPoint(100, 100))

            node2 = view.add_node(node.ConstNode, 'node2')
            node2.set_position(QPoint(100, 200))

            node3 = view.add_node(node.AddNode, 'node3')
            node3.set_position(QPoint(300, 150))

            const1_text = QLineEdit()
            const2_text = QLineEdit()
            calc_button = QPushButton(u'計算')
            result_text = QLineEdit()

            def _calc():
                input1 = float(const1_text.text())
                node1.model.set_data(input1)

                input2 = float(const2_text.text())
                node2.model.set_data(input2)

                node3.model.evaluate()
                result_text.setText(str(node3.model.output.value))

            calc_button.clicked.connect(_calc)

            layout = hbox(
                view,
                vbox(
                    hbox(QLabel(u'入力1'), const1_text),
                    hbox(QLabel(u'入力2'), const2_text),
                    hline(),
                    hbox(calc_button, result_text),
                    stretch()
                )
            )

            widget = QWidget()
            widget.setLayout(layout)

            self.setCentralWidget(widget)

    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
