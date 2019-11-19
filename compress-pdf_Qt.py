import os
import sys
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QInputDialog, QFileDialog
from PyQt5.QtWidgets import QPushButton, QAction, QLineEdit, QMessageBox, QLabel


class Root(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setFixedSize(800, 500)
        self.title = "PDF-Compressor is an Open Source Project by IT'S FOSS"
        self.top = 100
        self.left = 100
        self.width = 800
        self.height = 500
        self.InitWindow()

    def InitWindow(self):

        self.setWindowIcon(QtGui.QIcon("its.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.button = QPushButton('Select File', self)
        self.button.clicked.connect(self.select_pdf)
        self.button.move(200, 250)

        self.button2 = QPushButton('Compress', self)
        self.button2.clicked.connect(self.compress)
        self.button2.move(500, 250)

        self.image = QLabel(self)
        self.image.setPixmap(QtGui.QPixmap("pdff.png"))
        self.image.resize(100, 100)
        self.image.move(230, 150)
        self.image.show()

        self.image2 = QLabel(self)
        self.image2.setPixmap(QtGui.QPixmap("inboxx.png"))
        self.image2.resize(100, 100)
        self.image2.move(525, 150)
        self.image2.show()

        self.image3 = QLabel(self)
        self.image3.setPixmap(QtGui.QPixmap("its.png"))
        self.image3.resize(50, 50)
        self.image3.move(180, 385)
        self.image3.show()

        self.label = QLabel(self)
        self.label.setText("PDF-Compressor is an Open Source Project by It's FOSS")
        self.label.move(250, 400)
        self.label.resize(400, 20)

        self.show()

    def select_pdf(self):
        self.file = QFileDialog.getOpenFileName(self, "Select a Pdf File", "/home/", "Pdf Files (*.pdf)")[0]
        self.filek = self.file.replace(" ", "-")
        self.filepath = open('input.txt', 'w')
        with self.filepath:
            self.button.setText(os.path.basename(self.filek))
            self.filepath.write(self.filek)
        self.button2.setStyleSheet("background-color: green ")


    def compress(self):
        print("#")
        command = subprocess.Popen(['bash', 'compress-button.sh'])


App = QApplication(sys.argv)
root = Root()
sys.exit(App.exec())
