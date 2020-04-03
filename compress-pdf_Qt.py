import os
from os.path import basename
import sys
import subprocess
import PyQt5
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QInputDialog, QFileDialog
from PyQt5.QtWidgets import QPushButton, QRadioButton, QAction, QLineEdit, QMessageBox, QLabel


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
        self.button2.clicked.connect(lambda:self.compress(self.radio1.isChecked()))
        self.button2.clicked.connect(self.exists)
        self.button2.move(500, 250)
        self.button2.setEnabled(False)
        self.button2.setStyleSheet("background-color: #808080; ")

        self.radio1 = QRadioButton('Low Compression', self)
        self.radio1.move(330, 180)
        self.radio1.resize(200, 20)
        self.radio1.setChecked(True)

        self.radio2 = QRadioButton('Medium Compression', self)
        self.radio2.move(330, 210)
        self.radio2.resize(200, 20)

        self.radio3 = QRadioButton('High Compression', self)
        self.radio3.move(330, 240)
        self.radio3.resize(200, 20)

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
        self.button.setText(os.path.basename(self.file))
        if self.button.text() == '':
            self.button.setText("Select File")
            self.button2.setEnabled(False)
            self.button2.setStyleSheet("background-color: #808080; ")
        else:
            self.button2.setStyleSheet("background-color: green ")
            self.button2.setEnabled(True)

    def compress(self, check):
        if check:
            subprocess.call(['bash', 'compress-button.sh', '-l', self.file])
        if check == self.radio2.isChecked():
            subprocess.call(['bash', 'compress-button.sh', '-x', self.file])
        if  check == self.radio3.isChecked():
            subprocess.call(['bash', 'compress-button.sh', '-m', self.file])

    def exists(self):
        self.answer = subprocess.call(['bash', 'out.sh'])
        if self.answer == 0:
            self.msg = QMessageBox()
            self.msg.setText("Your file has been compressed.")
            self.msg.show()
        else:
            self.msg = QMessageBox()
            self.msg.setText("Something went Wrong")
            self.msg.show()

App = QApplication(sys.argv)
root = Root()
sys.exit(App.exec())
