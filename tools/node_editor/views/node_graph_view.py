# coding: utf-8
from __future__ import absolute_import
from typing import *

from gui.pyside_modules import *
from gui.layouts import *
from gui.widgets import *

from tools.node_editor.views.node_item import NodeItem
from tools.node_editor.views.graphics_view import GraphicsView
from tools.node_editor.nodes.node import ConstNode, AddNode


class NodeGraphView(GraphicsView):

    def __init__(self, parent=None):
        super(NodeGraphView, self).__init__(parent)
        self.mouse_move.connect(self.on_mouse_move)
        self.mouse_wheel.connect(self.on_mouse_wheel)

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


class NodeGraphScene(QGraphicsScene):

    def __init__(self, *args, **kwargs):
        super(NodeGraphScene, self).__init__(*args, **kwargs)
        self.__mouse_overed_items = set()

    def add_node(self, cls, name):
        # type: (type, str) -> NodeItem
        model = cls(name)
        model.initialize()
        node = NodeItem(self, name, model)
        return node

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

        super(NodeGraphScene, self).mouseMoveEvent(e)


if __name__ == '__main__':
    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            scene = NodeGraphScene(0, 0, 640, 480)
            scene.addRect(0, 0, scene.width(), scene.height(), QPen(Qt.transparent), QBrush(Qt.white))

            node1 = scene.add_node(ConstNode, 'node1')
            node1.set_position(QPoint(100, 100))

            node2 = scene.add_node(ConstNode, 'node2')
            node2.set_position(QPoint(100, 200))

            node3 = scene.add_node(AddNode, 'node3')
            node3.set_position(QPoint(300, 150))

            view = NodeGraphView()
            view.setBackgroundBrush(QBrush(Qt.gray))
            view.setScene(scene)

            const1_text = QLineEdit()
            const2_text = QLineEdit()
            calc_button = QPushButton(u'計算')
            result_text = QLineEdit()

            def _calc():
                input1 = float(const1_text.text())
                print ('set: {}, {}'.format(node1.model.name, input1))
                node1.model.set_data(input1)

                input2 = float(const2_text.text())
                print ('set: {}, {}'.format(node2.model.name, input2))
                node2.model.set_data(input2)

                # NodeGraph.evaluate(node3.model)
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
