import sys
import ctypes
import random
import numpy as np

import concurrent.futures

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class main_application(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("assets/icon.png"))
        # Setzen des Icons
        my_app_id = 'by_Müller_Willi.Game_of_Life.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

        self.setWindowTitle('Game_of_Life')

        self.scale = 1.5

        self.height = int(1080 * self.scale)
        self.width = int(1920 * self.scale)

        self.resize(self.width, self.height)
        self.setMinimumSize(self.width, self.height)

        self.figures = QLabel(self)
        self.fill_color = QColor(255, 255, 255)

        self.stop = False
        self.tile_size = 1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animation)
        self.speed = 100
        self.timer.start(self.speed)

        self.cells = np.zeros((self.height // self.tile_size, self.width // self.tile_size), dtype=np.uint8)
        self.draw_cells = {}

        self.get_cells()

        self.setWindowTitle(str(self.speed))

    def get_cells(self):
        id = 0
        self.cells.fill(0)
        self.draw_cells = {}
        for y in range(self.height // self.tile_size):
            for x in range(self.width // self.tile_size):
                if random.random() < random.uniform(0.1, 0.01):
                    self.cells[y, x] = 1
                    self.draw_cells[id] = [y, x]
                id += 1


    def animation(self):

        self.setWindowTitle(str(self.speed))

        # Calculate the number of neighbors for each cell using a 3x3 neighborhood sum filter
        neighbors_count = np.zeros_like(self.cells, dtype=np.uint8)
        neighbors_count += np.roll(self.cells, (-1, -1), axis=(0, 1))
        neighbors_count += np.roll(self.cells, (-1, 0), axis=(0, 1))
        neighbors_count += np.roll(self.cells, (-1, 1), axis=(0, 1))
        neighbors_count += np.roll(self.cells, (0, -1), axis=(0, 1))
        neighbors_count += np.roll(self.cells, (0, 1), axis=(0, 1))
        neighbors_count += np.roll(self.cells, (1, -1), axis=(0, 1))
        neighbors_count += np.roll(self.cells, (1, 0), axis=(0, 1))
        neighbors_count += np.roll(self.cells, (1, 1), axis=(0, 1))

        # Apply the Game of Life rules to update the cells
        survive_mask = np.logical_and(self.cells == 1, np.logical_or(neighbors_count == 2, neighbors_count == 3))
        birth_mask = np.logical_and(self.cells == 0, neighbors_count == 3)
        self.cells = np.logical_or(survive_mask, birth_mask).astype(np.uint8)

        # Update the draw_cells dictionary with the new live cells
        self.draw_cells = {}
        indices = np.argwhere(self.cells == 1)
        for id, (y, x) in enumerate(indices):
            self.draw_cells[id] = [y, x]

        self.update()

    def paintEvent(self, event):
        self.setWindowTitle(str(self.speed))
        canvas = QPixmap(self.width, self.height)
        canvas.fill(QColor(0, 0, 0, 255))
        self.figures.setPixmap(canvas)
        self.figures.setGeometry(0, 0, self.width, self.height)

        painter_figures = QPainter(self.figures.pixmap())

        for cell in self.draw_cells.values():
            rect = QRect(cell[1] * self.tile_size, cell[0] * self.tile_size, self.tile_size, self.tile_size)
            painter_figures.fillRect(rect, self.fill_color)            

        painter_figures.end()

        self.figures.update()


    def keyPressEvent(self, event):
        key = event.key()

        # stop sim
        if key == Qt.Key_E:
            if not self.stop:
                self.timer.stop()
                self.stop = True
            else:
                self.stop = False
                self.timer.start(self.speed)

        # speedup sim
        if key == Qt.Key_W:
            self.speed += 1
            if not self.stop:
                self.timer.start(self.speed)
            self.update()

        # speeddown sim
        if key == Qt.Key_S:
            if self.speed - 1 >= 0:
                self.speed -= 1
            if not self.stop:
                self.timer.start(self.speed)
            self.update()

        # reset
        if key == Qt.Key_R:
            self.get_cells()

        # exit
        if key == Qt.Key_Escape:
            sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = main_application()
    application.show()
    sys.exit(app.exec_())
