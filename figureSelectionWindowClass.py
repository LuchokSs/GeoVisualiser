import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog

from exceptions import DataBaseException

from secondary import FigureView, Model, Point, MovingDialog


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
        """Метод для демонстрации списка фигур."""

        for figure in self.figureNames:
            path = self.db.execute(f"""SELECT figureImagePath FROM figure
                                           WHERE figureName='{figure}'""").fetchall()[0][0]
            self.figuresLayout.addWidget(FigureView(self, path, figure))

    def update_model(self):
        """Метод добавления выбранной фигуры к текущему рисунку."""

        senderBtn = self.sender()
        dialog = MovingDialog(self)
        result = dialog.exec_()
        if result == 1:
            results = dialog.xValue.value(), dialog.yValue.value(), dialog.yValue.value()
        elif result == 0:
            self.destroy()
            return
        updatedModel = Model()
        loaded = self.db.execute(f"""SELECT pointName, xcrd, ycrd, zcrd FROM points
                                        WHERE figureID=(
                                            SELECT figureID FROM figure
                                                WHERE figureName=('{senderBtn.figureName}'))""").fetchall()
        stv = {}
        for i in range(len(loaded)):
            self.starter.pointInput.setText(loaded[i][0] + ' '
                                            + ','.join([str(loaded[i][1] + results[0]),
                                                        str(loaded[i][2] + results[1]),
                                                        str(loaded[i][3] + results[1])]))
            stv[loaded[i][0]] = self.starter.add_point_to_list()
        pnts = self.db.execute(f"""SELECT pointOneID, pointTwoID FROM connections 
                                                WHERE figureID=(
                                                    SELECT figureID FROM figure
                                                        WHERE figureName=('{senderBtn.figureName}'))""").fetchall()
        for i in range(len(pnts)):
            loaded = self.db.execute(f"""SELECT pointName FROM points
                                            WHERE pointID in ({pnts[i][0]}, {pnts[i][1]})""").fetchall()
            updatedModel.connections.append([stv[loaded[0][0]], stv[loaded[1][0]]])
            self.starter.model.connections.append([stv[loaded[0][0]], stv[loaded[1][0]]])
        self.starter.redraw()
        self.destroy()
