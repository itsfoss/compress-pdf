from PySide2.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QRadioButton,
    QMenuBar,
    QAction,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QButtonGroup
)
from PySide2.QtCore import Qt
from PySide2.QtGui import (
    QKeySequence,
    QPixmap,
    QIcon
)

class HomeLayout(QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.setContentsMargins(15, 15, 15, 15)

    def addItem(self, itemName, item):
        setattr(self, itemName, item)
        self.addWidget(item)

    def addItems(self, items: list):

        for itemName, item in items:
            self.addItem(itemName, item)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setupUI()


    # Event handling is done here now
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
        
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def setupUI(self):

        self.setWindowTitle("PDF-Compressor")
        self.setWindowIcon(QIcon(QPixmap("resources/its.png")))

        self.menuBar = self.menuBar()
        self.file = self.menuBar.addMenu("&File")
        self.edit = self.menuBar.addMenu("&Edit")
        self.help = self.menuBar.addMenu("&Help")


        # File
        self.addFiles = QAction("Add files")
        self.addFiles.setShortcut(QKeySequence("Ctrl+f"))
        self.file.addAction(self.addFiles)
        self.preferences = QAction("Preferences")
        self.preferences.setShortcut(QKeySequence("Ctrl+p"))
        self.file.addAction(self.preferences)
        self.quit = QAction("Quit")
        self.quit.setShortcut(QKeySequence("Ctrl+q"))
        self.file.addAction(self.quit)

        # Edit
        self.remove = QAction("Remove")
        self.remove.setShortcut(QKeySequence("Ctrl+r"))
        self.edit.addAction(self.remove)

        # Help
        self.donate = QAction("Donate")
        self.contribute = QAction("Contibute")
        self.aboutUs = QAction("About us")
        self.help.addAction(self.donate)
        self.help.addAction(self.contribute)
        self.help.addAction(self.aboutUs)

        # By default "remove" is disabled
        self.remove.setDisabled(True)

        # The base layout is vertical
        self.centralWidget = QWidget()
        self.centralLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.centralLayout)
        #Placeholder for the top with itsfoss icon
        self.topIcon = QLabel()
        self.topIcon.setPixmap(QPixmap("resources/its.png"))
        self.topIcon.setAlignment(Qt.AlignCenter)
        self.topIcon.setMargin(15)
        self.centralLayout.addWidget(self.topIcon)

        # Main layout
        self.mainLayout = QHBoxLayout()
        self.centralLayout.addLayout(self.mainLayout)

        # Now we need HBox layouts for three columns
        self.leftLayout = HomeLayout()
        self.midLayout = HomeLayout()
        self.rightLayout = HomeLayout()

        # left layout 
        self.leftLayout.addItems([
            ("iconLabel", QLabel()),
            ("addFiles", QPushButton("Add files")),
            ("browse", QPushButton("Browse"))
        ])
        self.leftLayout.iconLabel.setPixmap(QPixmap("resources/pdff.png"))
        self.leftLayout.iconLabel.setAlignment(Qt.AlignCenter)

        # Mid layout
        self.midLayout.addItems([
            ("lowLevel", QRadioButton("low compression")),
            ("midLevel", QRadioButton("mid compression")),
            ("highLevel", QRadioButton("high compression"))
        ])
        self.midLayout.buttonGroup = QButtonGroup()
        self.midLayout.buttonGroup.addButton(
            self.midLayout.lowLevel)
        self.midLayout.buttonGroup.addButton(
            self.midLayout.midLevel)
        self.midLayout.buttonGroup.addButton(
            self.midLayout.highLevel)
        
        # right layout
        self.rightLayout.addItems([
            ("iconLabel", QLabel()),
            ("compressButton", QPushButton("Compress"))
        ])
        self.rightLayout.iconLabel.setPixmap(QPixmap("resources/inboxx.png"))
        self.rightLayout.iconLabel.setAlignment(Qt.AlignCenter)
        self.rightLayout.compressButton.setDisabled(True)
            

        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.midLayout)
        self.mainLayout.addLayout(self.rightLayout)


        self.bottomLabel = QLabel("PDF Compressor is an Open Source project by It's FOSS")
        self.bottomLabel.setAlignment(Qt.AlignCenter)
        self.bottomLabel.setMargin(15)
        self.centralLayout.addWidget(self.bottomLabel)
        
        
        self.setCentralWidget(self.centralWidget)

        



if __name__ == "__main__":

    from PySide2.QtWidgets import QApplication
    app = QApplication([])
    window = MainWindow()
    window.show()
    import sys
    sys.exit(app.exec_())