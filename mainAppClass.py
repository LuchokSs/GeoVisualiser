from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QInputDialog, QDialog
from numpy import matmul as mult, array

from PIL import Image, ImageDraw

from math import cos, sin, pi

import json_tricks as json

import sqlite3

from secondary import Point, Model, set_img, ADDialog

from figureSelectionWindowClass import FigureSelectionWindow

from exceptions import *


class MainWindow(QMainWindow):
    def __init__(self, starter=None, model=Model()):
        super().__init__()
        uic.loadUi('geoVisualiser.ui', self)

        self.starter = starter

        self.figuresDataBase = "figuresDataBase.db"

        self.model = model
        self.update_model()

        self.field = Image.new('RGB', (700, 700), (255, 255, 255))

        self.pointPressed = ''
        self.systemPoints = [Point([0, 0, 0]),

                             Point([0, 0, -300]),  # Ось Z
                             Point([0, 0, 300]),

                             Point([0, 300, 0]),  # Ось Y
                             Point([0, -300, 0]),

                             Point([300, 0, 0]),  # Ось X
                             Point([-300, 0, 0]),

                             Point([320, 0, 0]),  # X
                             Point([0, 320, 0]),  # Y
                             Point([0, 0, 320])]  # Z
        self.lastAxis = 'x'
        self.redraw()

        set_img(self, self.field)

        self.addButton.clicked.connect(self.add_point_to_list)
        self.connectPoints.clicked.connect(self.add_connected_points)
        self.disconnectPoints.clicked.connect(self.del_connected_points)
        self.delButton.clicked.connect(self.del_point_from_list)
        self.endChanging.clicked.connect(self.change_crd_of_point)
        self.exitButton.clicked.connect(self.open_start_window)
        self.saveFile.clicked.connect(self.save)
        self.loadFigureButton.clicked.connect(self.load_figure)
        self.saveFigureButton.clicked.connect(self.save_figure)

        self.pointList.itemPressed.connect(self.item_pressed)

        self.xRotate.valueChanged.connect(self.redraw)
        self.yRotate.valueChanged.connect(self.redraw)
        self.zRotate.valueChanged.connect(self.redraw)

        self.pointOne.currentTextChanged.connect(self.current_text_changed)
        self.pointTwo.currentTextChanged.connect(self.current_text_changed)

    def update_model(self):
        """Метод для формирования начального рисунка в случае, если был открыт существующий файл."""
        self.connectionsText = {self.pointOne: '',
                                self.pointTwo: ''}
        for literal in self.model.points.keys():
            self.pointList.addItem(literal + ' ' + ','.join(list(map(str, self.model.points[literal].coordinates))))
            self.pointList.sortItems()
            self.pointOne.addItem(literal)
            self.pointTwo.addItem(literal)
            if self.connectionsText[self.pointOne] == '':
                self.connectionsText = {self.pointOne: literal,
                                        self.pointTwo: literal}

    def add_point_to_list(self):
        """Метод добавления точки."""
        if self.pointInput.text() != '':
            literal = self.pointInput.text().split()[0]
            try:
                if len(self.pointInput.text().split()) != 2:
                    raise InputSyntaxException
                if len(self.pointInput.text().split()[1].split(',')) != 3:
                    raise InputSyntaxException
                if self.pointInput.text().split()[0] not in self.model.points.keys():
                    self.model.points[literal] = self.pointInput.text().split()[1]
                else:
                    self.model.points[literal + f'{list(self.model.points.keys()).count(literal)}'] \
                        = self.pointInput.text().split()[1]
            except InputSyntaxException:
                self.pointInput.setText('ОШИБКА ВВОДА')
                return
            literal = list(self.model.points.keys())[-1]

            self.pointList.addItem(literal + ' ' + (self.model.points[literal]))
            self.pointList.sortItems()
            self.pointOne.addItem(literal)
            self.pointTwo.addItem(literal)

            self.model.points[literal] = Point(list(map(int, self.model.points[literal].strip('()').split(','))),
                                               literal)

            self.pointInput.setText('')

        self.redraw()

    def del_point_from_list(self):
        """Метод для удаления точки."""
        if self.pointPressed != '':
            dialog = ADDialog()
            if not dialog.exec_():
                return
            try:
                self.pointList.takeItem(self.pointList.row(self.pointPressed))
                self.model.points.pop(self.pointPressed.text().split()[0])
                self.pointOne.clear()
                self.pointTwo.clear()
                try:
                    i = 0
                    while i < len(self.model.connections):
                        if self.pointPressed.text().split()[0] in self.model.connections[i]:
                            del self.model.connections[i]
                            i -= 1
                        i += 1
                except ValueError:
                    pass
                for i in self.model.points:
                    self.pointOne.addItem(i[0])
                    self.pointTwo.addItem(i[0])
            except KeyError:
                pass

        self.redraw()

    def add_connected_points(self):
        """Метод для соединения точек."""
        if self.connectionsText[self.pointOne] != '' and self.connectionsText[self.pointTwo] != '':
            if [min(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo]),
                max(self.connectionsText[self.pointOne],
                    self.connectionsText[self.pointTwo])] not in self.model.connections:
                self.model.connections.append(
                    [min(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo]),
                     max(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo])])
            self.redraw()

    def del_connected_points(self):
        """Метод для разъединения точек."""
        try:
            try:
                del self.model.connections[self.model.connections.index(
                    [min(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo]),
                     max(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo])])]
            except Exception:
                raise PointExistingException
        except PointExistingException:
            return
        self.redraw()

    def load_figure(self):
        """Метод для загрузки фигуры из окна figureSelection."""
        self.figureSelection = FigureSelectionWindow(self.figuresDataBase, starter=self)
        self.figureSelection.show()

    def draw_line(self, p1, p2, line='common', color='#bF311A'):
        """Метод для рисования линии."""
        drawer = ImageDraw.Draw(self.field)
        point1 = p1.crds()
        point2 = p2.crds()

        if line == 'common':
            drawer.line(((self.convert_system(point1)), self.convert_system(point2)), color, width=3)
        elif line == 'splited':
            start = point1
            add = list(map(lambda x: x // 10, self.vector(point1, point2)))
            i = 0
            while self.vector_lenth(start, point1) < self.vector_lenth(start, point2):
                if (i % 2 == 0 and self.vector_lenth(start, point2) - self.vector_lenth(start, point1)
                        > self.vector_lenth(start, point2) // 10):
                    drawer.line((self.convert_system(point1),
                                 (point1[0] - int(0.5 * point1[2]) + 350 + (add[0] - int(0.5 * add[2])),
                                  350 - (point1[1] - int(0.5 * point1[2])) - (add[1] - int(0.5 * add[2])))),
                                color, width=1)
                point1 = [point1[0] + add[0], point1[1] + add[1], point1[2] + add[2]]
                i += 1
        set_img(self, self.field)

    def current_text_changed(self, text):
        self.connectionsText[self.sender()] = text

    def item_pressed(self, item):
        """Метод для действий при выделении точки."""
        point = self.model.points[item.text().split()[0]]
        self.pointPressed = item
        self.rowPressed = self.pointList.currentRow()
        color = self.model.points[item.text().split()[0]].color
        self.model.points[item.text().split()[0]].set_color('#50AAAA')
        self.redraw()

        self.changeX.setValue(point.crds()[0])
        self.changeY.setValue(point.crds()[1])
        self.changeZ.setValue(point.crds()[2])

        def func(a1, a2, a3, p1, p2, p3):
            self.draw_line(self.rotate(Point([a1, a2, a3]),
                                       self.xRotate.value(),
                                       self.zRotate.value(),
                                       self.yRotate.value()),
                           self.rotate(Point([p1, p2, p3]),
                                       self.xRotate.value(),
                                       self.zRotate.value(),
                                       self.yRotate.value()), line='splited', color='#50AAAA')

        if point[0] and point[1] and point[2]:
            func(point[0], point[1], point[2], point[0], point[1], 0)
            func(point[0], point[1], 0, point[0], 0, 0)
            func(point[0], point[1], 0, 0, point[1], 0)

            func(point[0], point[1], point[2], point[0], 0, point[2])
            func(point[0], 0, point[2], point[0], 0, 0)
            func(point[0], 0, point[2], 0, 0, point[2])

            func(point[0], point[1], point[2], 0, point[1], point[2])
            func(0, point[1], point[2], 0, 0, point[2])
            func(0, point[1], point[2], 0, point[1], 0)
        elif point[0] and point[1] and not point[2]:
            func(point[0], point[1], 0, point[0], 0, 0)
            func(point[0], point[1], 0, 0, point[1], 0)
        elif point[0] and not point[1] and point[2]:
            func(point[0], point[1], point[2], 0, 0, point[2])
            func(point[0], point[1], point[2], point[0], 0, 0)
        elif not point[0] and point[1] and point[2]:
            func(point[0], point[1], point[2], 0, 0, point[2])
            func(point[0], point[1], point[2], 0, point[1], 0)
        self.model.points[item.text().split()[0]].set_color(color)

    def change_crd_of_point(self):
        """Метод для изменения координат точки."""
        if self.pointPressed == '':
            return
        try:
            point = self.model.points[self.pointPressed.text().split()[0]]
        except Exception:
            raise PointExistingException
        point.coordinates = [self.changeX.value(), self.changeY.value(), self.changeZ.value()]
        crds = point.crds()
        self.pointList.takeItem(self.rowPressed)
        self.pointList.addItem(self.pointPressed.text().split()[0] + f' {crds[0]},{crds[1]},{crds[2]}')
        self.pointList.sortItems()
        self.changeX.setValue(0)
        self.changeY.setValue(0)
        self.changeZ.setValue(0)
        self.redraw()

        self.pointPressed = ''

    def rotate(self, point, x, y, z):
        """Метод для реализации поворота точек вокруг осей фигуры."""
        angleX, angleY, angleZ = (x / 180 * pi), (y / 180 * pi), (z / 180 * pi)
        newPoint = self.multiply([[1, 0, 0],
                                  [0, cos(angleX), sin(angleX)],
                                  [0, -sin(angleX), cos(angleX)]],
                                 [[cos(angleZ), -sin(angleZ), 0],
                                  [sin(angleZ), cos(angleZ), 0],
                                  [0, 0, 1]])
        newPoint = self.multiply(newPoint,
                                 [[cos(angleY), 0, sin(angleY)],
                                  [0, 1, 0],
                                  [-sin(angleY), 0, cos(angleY)]])
        newPoint = Point(self.multiply(newPoint, point.crds()))
        return newPoint

    def redraw(self):
        """Метод для перерисовки поля."""
        drawer = ImageDraw.Draw(self.field)
        drawer.polygon(((0, 0), (0, 700), (700, 700), (700, 0)), "#FFFFFF")
        self.newPoints = {}
        self.newSystem = []
        try:
            for i in self.model.points.keys():
                self.newPoints[i] = self.rotate(self.model.points[i], self.xRotate.value(), self.zRotate.value(),
                                                self.yRotate.value())
                self.newPoints[i].set_color(self.model.points[i].color)
        except Exception:
            raise PointExistingException
        for point in self.systemPoints:
            self.newSystem.append(self.rotate(point, self.xRotate.value(), self.zRotate.value(), self.yRotate.value()))
        if self.freezeSystem.isChecked():
            self.newSystem = self.systemPoints
        self.draw_system()
        for points in self.model.connections:
            self.draw_line(self.newPoints[points[0]], self.newPoints[points[1]])
        for point in self.newPoints.keys():
            color = self.newPoints[point].color
            point = self.newPoints[point].crds()
            drawer.ellipse(
                ((point[0] - int(0.5 * point[2]) - 3 + 350, 350 - (point[1] - int(0.5 * point[2])) - 3),
                 (point[0] - int(0.5 * point[2]) + 3 + 350, 350 - (point[1] - int(0.5 * point[2])) + 3)),
                color)
        set_img(self, self.field)

    def draw_system(self):
        """Вспомогательный метод для рисования системы координат."""
        drawer = ImageDraw.Draw(self.field)
        point2 = (0, 0, 0)
        for point1 in self.newSystem[1:7]:
            point1 = point1.crds()
            drawer.line(((point1[0] - int(0.5 * point1[2]) + 350, 350 - (point1[1] - int(0.5 * point1[2]))),
                         (point2[0] - int(0.5 * point2[2]) + 350, 350 - (point2[1] - int(0.5 * point2[2])))),
                        "#000000", width=3)
        drawer.text((self.convert_system(self.newSystem[7].crds())), 'X', "#000000")
        drawer.text((self.convert_system(self.newSystem[8].crds())), 'Y', "#000000")
        drawer.text((self.convert_system(self.newSystem[9].crds())), 'Z', "#000000")

    def open_start_window(self):
        """Метод для выхода к стартовому окну."""
        self.starter.show()
        self.destroy()

    def convert_system(self, point):
        """Вспомогательный метод преобразования 3-х мерных координат в 2-х мерные."""
        return point[0] - int(0.5 * point[2]) + 350, 350 - (point[1] - int(0.5 * point[2]))

    def vector_lenth(self, p1, p2):
        """Вспомогательный метод для вычисления длины вектора."""
        return (((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2) + ((p2[2] - p1[2]) ** 2)) ** 0.5

    def vector(self, p1, p2):
        """Вспомогательный метод для вычисления вектора между двумя точками."""
        return [int(p2[0]) - int(p1[0]), int(p2[1]) - int(p1[1]), int(p2[2]) - int(p1[2])]

    def multiply(self, a, b):
        """Вспомогательный метод для умножения матриц."""
        a = array(a)
        b = array(b)
        res = mult(a, b)
        resList = []
        try:
            for i in range(len(res)):
                resList.append([])
                for g in range(len(res[i])):
                    resList[i].append(res[i][g])
        except TypeError:
            for i in range(len(res)):
                resList.append(res[i])
            resList = resList[1:]

        return resList

    def save(self):
        """Метод для сохранения файла рисунка."""
        path = QFileDialog.getSaveFileName(self, 'Сохранить как...', '', 'График (*.json);; Картинка (*.png)')
        try:
            if path[1] == "График (*.json)":
                with open(path[0], 'w') as outfile:
                    json.dump(self.model, outfile)
                return
            if path[1] == "Картинка (*.png)":
                self.field.save(path[0])
        except ValueError as er:
            print(er)

    def save_figure(self):
        """Метод для сохранения файла фигуры."""
        name, ok_pressed = QInputDialog.getText(self, "Введите название файла", "ВВедите название файла...")
        if not ok_pressed:
            return
        path = './data/' + name + '.png'
        try:
            self.field.save(path)
        except ValueError:
            return
        db = sqlite3.connect(self.figuresDataBase)
        cursor = db.cursor()
        cursor.execute(f"""INSERT INTO figure(figureName, figureImagePath) VALUES('{name}', '{path}')""")
        db.commit()
        figureID = cursor.execute(f"""SELECT figureID FROM figure
                                      WHERE figureName='{name}'""").fetchall()[0][0]
        for pointName in self.model.points.keys():
            point = self.model.points[pointName].crds()
            cursor.execute(f"""INSERT INTO points('figureID', 'pointName', 'xcrd', 'ycrd', 'zcrd') VALUES(
                                    '{figureID}', '{pointName}', '{point[0]}', '{point[1]}', '{point[2]}')""")
            db.commit()
        for connection in self.model.connections:
            pointOneID = cursor.execute(f"""SELECT pointID FROM points
                                            WHERE pointName='{connection[0]}'""").fetchall()[0][0]
            pointTwoID = cursor.execute(f"""SELECT pointID FROM points
                                            WHERE pointName='{connection[1]}'""").fetchall()[0][0]
            cursor.execute(f"""INSERT INTO connections('figureID', 'pointOneID', 'pointTwoID') VALUES(
                                    '{figureID}', '{pointOneID}', '{pointTwoID}')""")
            db.commit()
        db.close()
