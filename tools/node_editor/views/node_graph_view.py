# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *
from tools.node_editor.views.pyside_modules import *
from tools.node_editor.views.node_item import *
from tools.node_editor.views.graphics_view import *


class NodeGraphView(GraphicsView):

    def __init__(self, parent=None):
        super(NodeGraphView, self).__init__(parent)
        self.mouse_move.connect(self.on_mouse_move)
        self.mouse_wheel.connect(self.on_mouse_wheel)

    def on_mouse_wheel(self, wheel):
        # type: (MouseWheelEventArgs) -> NoReturn
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

            if move.buttons() == Qt.RightButton:
                self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
                delta_x = move.delta_pos.x()
                scale = 1.0 + delta_x * 0.001
                transform.scale(scale, scale)

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

    def add_node(self):
        node = NodeItem()
        self.addItem(node)
        return node


if __name__ == '__main__':
    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            scene = NodeGraphScene(0, 0, 640, 480)
            scene.addRect(0, 0, scene.width(), scene.height(), QPen(Qt.transparent), QBrush(Qt.white))

            node1 = scene.add_node()
            node1.set_position(QPointF(100, 100))

            node2 = scene.add_node()
            node2.set_position(QPointF(300, 100))

            conn1 = node1.connect(node2)

            view = NodeGraphView()
            view.setBackgroundBrush(QBrush(Qt.gray))
            view.setScene(scene)

            self.setCentralWidget(view)

    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
