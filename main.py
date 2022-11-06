from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from PIL import Image

import sys

import json_tricks as json

from mainAppClass import MainWindow

from exceptions import FilesDoNotComplited


class StartingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('StartingWindow.ui', self)
        try:
            self.testerCat = Image.open('./data/satisfied_cat.PNG')
        except FileNotFoundError:
            raise FilesDoNotComplited("Check files")
        except PermissionError:
            raise FilesDoNotComplited("Check folders")

        self.mainApp = MainWindow(self)

        self.begButton.clicked.connect(self.open_chosen_file)
        self.createEmpty.clicked.connect(self.open_empty_file)
        self.choosePath.clicked.connect(self.choose_file)

    def open_app(self):
        '''Универсальный метод для открытия приложения.'''
        self.mainApp.show()
        self.hide()

    def open_chosen_file(self):
        """Метод для открытия файла с указанным путем."""
        try:
            with open(self.fileNameInput.text(), 'r') as loadfile:
                model = json.load(loadfile)
            self.mainApp = MainWindow(self, model)
            self.open_app()
        except FileNotFoundError:
            return
        except PermissionError:
            return

    def open_empty_file(self):
        """Метод для открытия пустого файла."""
        self.mainApp = MainWindow(self)
        self.open_app()

    def choose_file(self):
        """Метод для выбора пути к файлу"""
        self.path = QFileDialog.getOpenFileName(self, "Open file", '', 'Рисунок (*.json);; Все файлы (*)')[0]
        self.fileNameInput.setText(self.path)


if __name__ == '__main__':
    ex = QApplication(sys.argv)
    app = StartingWindow()
    app.show()
    sys.exit(ex.exec())
