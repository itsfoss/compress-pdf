from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout
)
from PySide2.QtCore import Qt

class Settings(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Settings - PDF Compressor")

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        

