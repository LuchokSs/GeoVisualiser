import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from exceptions import DataBaseException

from secondary import FigureView, Model, Point


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

        self.show_figures()

    def show_figures(self):
        for figure in self.figureNames:
            path = self.db.execute(f"""SELECT figureImagePath FROM figure
                                           WHERE figureName='{figure}'""").fetchall()[0][0]
            self.figuresLayout.addWidget(FigureView(self, path, figure))

    def update_model(self):
        senderBtn = self.sender()
        updatedModel = Model()
        loaded = self.db.execute(f"""SELECT pointName, xcrd, ycrd, zcrd FROM points
                                        WHERE figureID=(
                                            SELECT figureID FROM figure
                                                WHERE figureName=('{senderBtn.figureName}'))""").fetchall()
        for i in range(len(loaded)):
            updatedModel.points[loaded[i][0]] = Point([loaded[i][1], loaded[i][2], loaded[i][3]])
            self.starter.model.points[loaded[i][0]] = Point([loaded[i][1], loaded[i][2], loaded[i][3]])
        pnts = self.db.execute(f"""SELECT pointOneID, pointTwoID FROM connections 
                                                WHERE figureID=(
                                                    SELECT figureID FROM figure
                                                        WHERE figureName=('{senderBtn.figureName}'))""").fetchall()
        for i in range(len(pnts)):
            loaded = self.db.execute(f"""SELECT pointName FROM points
                                            WHERE pointID in ({pnts[i][0]}, {pnts[i][1]})""").fetchall()
            updatedModel.connections.append([loaded[0][0], loaded[1][0]])
            self.starter.model.connections.append([loaded[0][0], loaded[1][0]])
        self.starter.connectionsText = {self.starter.pointOne: '',
                                        self.starter.pointTwo: ''}
        for literal in updatedModel.points.keys():
            self.starter.pointList.addItem(literal +
                                           ' ' + ','.join(list(map(str, updatedModel.points[literal].coordinates))))
            self.starter.pointList.sortItems()
            self.starter.pointOne.addItem(literal)
            self.starter.pointTwo.addItem(literal)
            if self.starter.connectionsText[self.starter.pointOne] == '':
                self.starter.connectionsText = {self.starter.pointOne: literal,
                                                self.starter.pointTwo: literal}
        self.starter.redraw()
        self.destroy()
