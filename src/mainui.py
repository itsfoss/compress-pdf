from PySide2.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QRadioButton,
    QMenuBar,
    QAction,
    QVBoxLayout,
    QHBoxLayout
)
from PySide2.QtCore import Qt
from PySide2.QtGui import (
    QKeySequence,
    QPixmap,
    QIcon
)


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

        # By default "remove" is disabled
        self.remove.setDisabled(True)

        # The base layout is vertical
        self.mainLayout = QVBoxLayout()

        # Now we need HBox layouts for three columns
        



if __name__ == "__main__":

    from PySide2.QtWidgets import QApplication
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()