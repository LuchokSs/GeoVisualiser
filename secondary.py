from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic


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
        super().__init__(*args)
        uic.loadUi('FigureViewWidget.ui', self)
