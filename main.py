from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

import sys

import json_tricks as json

from mainAppClass import MainWindow


class StartingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('StartingWindow.ui', self)

        self.mainApp = MainWindow(self)

        self.begButton.clicked.connect(self.open_choosen_file)
        self.createEmpty.clicked.connect(self.open_empty_file)
        self.choosePath.clicked.connect(self.choose_file)

    def open_app(self):
        self.mainApp.show()
        self.hide()

    def open_choosen_file(self):
        try:
            with open(self.fileNameInput.text(), 'r') as loadfile:
                model = json.load(loadfile)
            self.mainApp = MainWindow(self, model)
            self.open_app()
        except FileNotFoundError:
            return

    def open_empty_file(self):
        self.mainApp = MainWindow(self)
        self.open_app()

    def choose_file(self):
        self.path = QFileDialog.getOpenFileName(self, "Open file", '', 'Рисунок (*.json);; Все файлы (*)')[0]
        self.fileNameInput.setText(self.path)


if __name__ == '__main__':
    ex = QApplication(sys.argv)
    app = StartingWindow()
    app.show()
    sys.exit(ex.exec())
