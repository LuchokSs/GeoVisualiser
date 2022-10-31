from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic

from PyQt5.QtGui import QPixmap
from PIL.ImageQt import ImageQt
from PIL import Image


def set_img(self, img):
    if str(type(img)) == "<class 'str'>":
        img = Image.open(img)
        img = img.resize((250, 250))
    self.pic = ImageQt(img)
    self.pixmap = QPixmap.fromImage(self.pic)
    self.picOutput.setPixmap(self.pixmap)


class Plane:
    def __init__(self, point1, point2, point3):
        self.corners = [point1, point2, point3]


class Point:
    def __init__(self, coordinates, name='SYS', color="#bF311A"):
        self.coordinates = list(map(int, coordinates))
        self.color = color
        self.name = name

    def __getitem__(self, key):
        return self.coordinates[key]

    def crds(self):
        return self.coordinates

    def set_color(self, color):
        self.color = color


class Model:
    def __init__(self):
        self.points = {}
        self.connections = []


class FigureView(QWidget):
    def __init__(self, *args):
        super().__init__(args[0])
        uic.loadUi('FigureViewWidget.ui', self)
        set_img(self, args[1])
        self.OKButton.figureName = args[2]
        self.OKButton.clicked.connect(args[0].update_model)
