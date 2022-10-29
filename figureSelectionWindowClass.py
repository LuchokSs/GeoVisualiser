import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from exceptions import DataBaseException

from secondary import FigureView


class FigureSelectionWindow(QMainWindow):
    def __init__(self, dataBase, starter=None):
        super().__init__()
        uic.loadUi('FigureSelectionWindow.ui', self)

        self.starter = starter
        try:
            if dataBase is None:
                raise DataBaseException
            self.db = sqlite3.connect(dataBase).cursor()
            self.figureNames = list(map(lambda x: x[0],
                                        self.db.execute("""SELECT figureName FROM figure""").fetchall()))
        except DataBaseException as er:
            print(er)

        self.showFigures()

    def showFigures(self):
        for figure in self.figureNames:
            path = self.db.execute(f"""SELECT figureImagePath FROM figure
                                           WHERE figureName='{figure}'""").fetchall()[0][0]
            self.figuresLayout.addWidget(FigureView(self, path))
