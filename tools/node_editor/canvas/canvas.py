# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *
from tools.node_editor.canvas.pyside_modules import *
from tools.node_editor.canvas.node_item import *


class Canvas(QGraphicsView):

    def __init__(self, scene, parent=None):
        super(Canvas, self).__init__(scene, parent)


if __name__ == '__main__':
    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            scene = QGraphicsScene(0, 0, 640, 480)

            node1 = NodeItem()
            node1.set_position(QPointF(10, 10))
            scene.addItem(node1)

            node2 = NodeItem()
            node2.set_position(QPointF(100, 100))
            scene.addItem(node2)

            conn1 = node1.connect(node2)
            scene.addItem(conn1)

            view = QGraphicsView()
            view.setBackgroundBrush(QBrush(Qt.gray))
            view.setScene(scene)

            self.setCentralWidget(view)

    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
