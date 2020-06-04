#! /usr/bin/env python3

import logging
import os
import signal
import subprocess
import sys
from re import search
import tempfile
import shutil

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QDialog, QButtonGroup
from PyQt5.QtWidgets import QPushButton, QRadioButton, QAction, QLineEdit, QMessageBox, QLabel

logging.basicConfig(level=logging.ERROR, format="%(message)s")
logger = logging.getLogger(__name__)

levels = {1: "prepress", 2:"screen", 3:"ebook"}

class Config:
    def __init__(self):
        self.cdir = os.environ["HOME"] + "/.config/compress-pdf"
        self.file = os.environ["HOME"] + "/.config/compress-pdf/config"
        self.file_exists = False
        self.lastdirstat = False
        self.outputfile = None
        self.lastdir = None
        if not os.path.isdir(self.cdir):
            os.mkdir(self.cdir, 0o755)
        if os.path.isfile(self.file):
            self.file_exists = True
            
    def getOutFileOpt(self):
        if self.file_exists:
            with open(self.file, 'r') as f:
                for line in f:
                    val = search("^OutputFilename +(auto|manual)", line)
                    if val != None:
                        self.outputfile = val.group(1).rstrip()
        return self.outputfile
        
    def getLastDirStat(self):
        if self.file_exists:
            with open(self.file, 'r') as f:
                for line in f:
                    val = search("^RememberLastDir +(true|false)", line)
                    if val != None:
                        if val.group(1).rstrip() == "true":
                            self.lastdirstat = True
        return self.lastdirstat
        
    def getLastDir(self):
        if self.file_exists:
            with open(self.file, 'r') as f:
                for line in f:
                    val = search("^LastDir +(.+) *\n*$", line)
                    if val != None:
                        self.lastdir = val.group(1).rstrip()
        return self.lastdir
        
    def setLastDir(self, dir):
        if self.lastdir == None:
            if self.getLastDir() == None:
                with open(self.file, 'a')  as f:
                    f.write(f"LastDir {dir}")
                    return 0
        _f = None
        with open(self.file, 'r') as f:
            _f = tempfile.NamedTemporaryFile(delete=False)
            for line in f:
                val = search("^LastDir +", line)
                if val != None:
                    _f.file.write(f"LastDir {dir}\n".encode("utf-8"))
                    continue
                _f.file.write(line.encode("utf-8"))
        _f.close()
        shutil.move(_f.name, self.file)
        

class Root(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_window()
        self.conf = Config()
        self.lastdir = (self.conf.getLastDir() if self.conf.getLastDirStat() else "/home/")
        self.outputfile = self.conf.getOutFileOpt()

    def init_window(self):
        self.setFixedSize(800, 500)
        self.title = "PDF-Compressor is an Open Source Project by IT'S FOSS"
        self.top = 100
        self.left = 100
        self.width = 800
        self.height = 500

        self.setWindowIcon(QtGui.QIcon("resources/its.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.button = QPushButton('Select File', self)
        self.button.clicked.connect(self.select_pdf)
        self.button.move(200, 250)

        self.button2 = QPushButton('Compress', self)
        self.button2.clicked.connect(lambda:self.compress(self.groupButton.checkedId()))
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

        self.groupButton = QButtonGroup()
        self.groupButton.addButton(self.radio1, 1)
        self.groupButton.addButton(self.radio2, 2)
        self.groupButton.addButton(self.radio3, 3)

        self.image = QLabel(self)
        self.image.setPixmap(QtGui.QPixmap("resources/pdff.png"))
        self.image.resize(100, 100)
        self.image.move(230, 150)
        self.image.show()

        self.image2 = QLabel(self)
        self.image2.setPixmap(QtGui.QPixmap("resources/inboxx.png"))
        self.image2.resize(100, 100)
        self.image2.move(525, 150)
        self.image2.show()

        self.image3 = QLabel(self)
        self.image3.setPixmap(QtGui.QPixmap("resources/its.png"))
        self.image3.resize(50, 50)
        self.image3.move(180, 385)
        self.image3.show()

        self.label = QLabel(self)
        self.label.setText("PDF-Compressor is an Open Source Project by It's FOSS")
        self.label.move(250, 400)
        self.label.resize(400, 20)

        self.label1 = QLabel(self)
        self.label1.setText("")
        self.label1.setStyleSheet("color: green; ")
        self.label1.move(320, 350)
        self.label1.resize(400, 20)

        self.label2 = QLabel(self)
        self.label2.setText("")
        self.label2.setStyleSheet("color: red; ")
        self.label2.move(320, 350)
        self.label2.resize(400, 20)

        self.label3 = QLabel(self)
        self.label3.setText("")
        self.label3.setStyleSheet("color: green; ")
        self.label3.move(320, 350)
        self.label3.resize(400, 40)

        self.label4 = QLabel(self)
        self.label4.setText("")
        self.label4.setStyleSheet("color: red; ")
        self.label4.move(320, 350)
        self.label4.resize(400, 40)

        self.font = QFont("Arial", 8)
        self.font.setBold(True)

        self.show()

    def select_pdf(self):
        self.file = QFileDialog.getOpenFileName(self, "Select a Pdf File", self.lastdir, "Pdf Files (*.pdf);; All Files (*.*)")[0]
        self.filename = os.path.split(self.file)
        self.conf.setLastDir(self.filename[0])
        self.button.setText(os.path.basename(self.file))
        self.button.setFont(self.font)
        self.label1.setText("Your file is ready to be compressed.")
        self.button2.setStyleSheet("background-color: green ")
        self.button2.setEnabled(True)
        if self.button.text() == '':
            self.label2.setText("PDF file has not been selected")
            self.label1.setText("")
            self.label3.setText("")
            self.label4.setText("")
            self.button2.setStyleSheet("background-color: red ")
            self.button2.setEnabled(False)
            self.button.setText("Select File")
        try:
            if self.file != '':
                if(os.path.splitext(self.file) == "pdf"):
                    self.label2.setStyleSheet("color: green; ")
                    self.label1.setText("Your file is ready to be compressed.")
                    self.label2.setText("")
                    self.label3.setText("")
                    self.label4.setText("")
                    self.button2.setStyleSheet("background-color: green ")
                else:
                    self.label2.setText("")
                    self.label3.setText("")
                    self.label4.setText("")
        except AttributeError:
                self.label2.setText("PDF file has not been selected.")

    def compress(self, check):
        logger.info("Starting compress method")
        if self.outputfile == "manual":
            self.output_file = QFileDialog.getSaveFileName(self, "Save File", self.filename[0], "Pdf Files (*.pdf);; All Files (*.*)")[0]
        elif self.ouputfile == "auto":
            self.output_file = self.file.replace(self.filename[1], self.filename[1].split('.')[0] + "-compressed.pdf")
        command = ["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", f"-dPDFSETTINGS=/{levels[check]}",
                "-dNOPAUSE", "-dQUIET", "-dBATCH", f'-sOutputFile="{self.output_file}"', f'"{self.file}"']
        out = subprocess.run(command, capture_output=True)
        try:
            out.check_returncode()
        except FileNotFoundError:
            self.error(out.stderr.decode("utf-8"), "Please install ghostscript")
        except subprocess.CalledProcessError:
            self.error(out.stderr.decode("utf-8"), out.stdout.decode("utf-8"))
        except Exception as e:
            self.error("error!", str(e))
        else:
            # Subprocess should fail if an error occurred.
            # If we end up here we can pull up the success page
            self.success("Your file has been compressed.\nIt coexists with your input file.")

    def success(self, msg):
        self.label1.setText("")
        self.label2.setText("")
        self.label3.setText(msg)
        self.label4.setText("")
    
    def error(self, title, msg):
        e = QMessageBox()
        e.setWindowTitle(title.rstrip())
        e.setText(msg.rstrip())
        e.exec_()

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    root = Root()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
