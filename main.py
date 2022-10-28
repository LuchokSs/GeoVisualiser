from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

import sys

import json_tricks as json

from mainApp import MainWindow


class StartingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('StartingWindow.ui', self)

        self.mainApp = MainWindow(self)

        self.begButton.clicked.connect(self.openChoosenFile)
        self.createEmpty.clicked.connect(self.openEmptyFile)
        self.choosePath.clicked.connect(self.chooseFile)

    def openApp(self):
        self.mainApp.show()
        self.hide()

    def openChoosenFile(self):
        try:
            with open(self.fileNameInput.text(), 'r') as loadfile:
                model = json.load(loadfile)
            self.mainApp = MainApp(self, model)
            self.openApp()
        except FileNotFoundError:
            return

    def openEmptyFile(self):
        self.mainApp = MainApp(self)
        self.openApp()

    def chooseFile(self):
        self.path = QFileDialog.getOpenFileName(self, "Open file", '', 'Рисунок (*.json);; Все файлы (*)')[0]
        self.fileNameInput.setText(self.path)


if __name__ == '__main__':
    ex = QApplication(sys.argv)
    app = StartingWindow()
    app.show()
    ex.exit(ex.exec())
