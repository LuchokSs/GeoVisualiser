from PyQt5.QtWidgets import QWidget, QLabel, QDialog, QPushButton
from PyQt5 import uic

from PyQt5.QtGui import QPixmap  # Скопируй 3 строки для set_img()
from PIL.ImageQt import ImageQt
from PIL import Image


def set_img(self, img):
    """Универсальный метод для установки картинки в Label с именем picOutput."""

    if str(type(img)) == "<class 'str'>":
        img = Image.open(img)
        img = img.resize((250, 250))
    self.pic = ImageQt(img)
    self.pixmap = QPixmap.fromImage(self.pic)
    self.picOutput.setPixmap(self.pixmap)


class Point:
    """Вспомогательный класс для хранения информации о точке."""

    def __init__(self, coordinates, name='SYS', color="#bF311A", pindex=0):
        self.coordinates = list(map(int, coordinates))
        self.color = color
        self.name = name
        self.index = pindex

    def __getitem__(self, key):
        """Метод для получения конкретной координаты точки."""
        return self.coordinates[key]

    def __str__(self):
        return ','.join([str(self.coordinates[0]), str(self.coordinates[1]), str(self.coordinates[2])])

    def crds(self):
        """Метод для получения координат точки в виде списка."""
        return self.coordinates

    def set_color(self, color):
        """Метод для изменения цвета точки."""
        self.color = color


class Model:
    """Модель, хранящая в себе всю информацию о рисунке."""

    def __init__(self):
        self.points = {}
        self.connections = []


class MovingDialog(QDialog):
    """Класс диалога передвижения добавляемой фигуры."""

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('movingDialog.ui', self)
        self.btnOK.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.reject)


class ADDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 500, 300, 90)
        self.setWindowTitle('Are you agree?')

        self.label = QLabel(self)
        self.label.setText('Point will be deleted')
        self.label.move(80, 10)

        self.btnOK = QPushButton(self)
        self.btnOK.setText('OK')
        self.btnOK.setGeometry(40, 30, 100, 50)

        self.btnCancel = QPushButton(self)
        self.btnCancel.setText('Cancel')
        self.btnCancel.setGeometry(160, 30, 100, 50)

        self.btnOK.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.reject)


class FigureView(QWidget):
    """Виджет, соединяющий рисунок точки и кнопку добавления."""

    def __init__(self, *args):
        super().__init__(args[0])
        uic.loadUi('FigureViewWidget.ui', self)
        set_img(self, args[1])
        self.OKButton.figureName = args[2]
        self.OKButton.clicked.connect(args[0].update_model)
