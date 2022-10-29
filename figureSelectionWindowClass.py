from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from PyQt5.QtGui import QPixmap
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

from exceptions import DataBaseException

from secondary import FigureView


class FigureSelectionWindow(QMainWindow):
    def __init__(self, dataBase, starter=None):
        super().__init__()
        uic.loadUi('FigureSelectionWindow.ui', self)

        self.starter = starter
        self.db = dataBase

        try:
            if self.db is None:
                raise DataBaseException
            with self.db.cursor() as cursor:
                self.figureNames = cursor.execute("""SELECT names FROM figures""").fetchall()
        except DataBaseException as er:
            print(er)

        self.figuresLayout.addItem(FigureView(self))
