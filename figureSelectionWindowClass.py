from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from PyQt5.QtGui import QPixmap
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt


class FigureSelectionWindow(QMainWindow):
    def __init__(self, dataBase, starter=None):
        super().__init__()
        uic.loadUi('FigureSelectionWindow.ui', self)

        self.starter = starter
        self.db = dataBase

        with self.db.cursor() as cursor:
            self.figureNames = cursor.execute("""SELECT names FROM figures""").fetchall()
