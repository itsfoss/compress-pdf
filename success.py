import os
import sys
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QInputDialog, QFileDialog
from PyQt5.QtWidgets import QPushButton, QAction, QLineEdit, QMessageBox, QLabel


class Success(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setFixedSize(300, 150)
        self.title = "Successful Compression"
        self.top = 100
        self.left = 100
        self.width = 200
        self.height = 200
        self.InitWindow()

    def InitWindow(self):

        self.setWindowIcon(QtGui.QIcon("its.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.label = QLabel(self)
        self.label.setText("Your file has been compressed.")
        self.label.move(50, 50)
        self.label.resize(400, 20)

        self.label2 = QLabel(self)
        self.label2.setText("It coexists with your input file.")
        self.label2.move(50, 70)
        self.label2.resize(400, 20)


        self.show()


App = QApplication(sys.argv)
root = Success()
sys.exit(App.exec())
