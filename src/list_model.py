from PySide2.QtWidgets import QListWidget, QListView
from PySide2.QtCore import Qt, QAbstractListModel, Signal
import os


class DataModel(QAbstractListModel):
    listChanged = Signal(int)

    def __init__(self):
        super().__init__()

        # set of dicts with the file names and paths
        self.items = set()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if self.config.showFullPath:
                return list(
                    x.get("path") for x in list(self.items)
                )
            else:
                return list(
                    x.get("name") for x in list(self.items)
                )
    
    def rowCount(self, index):
        return len (self.items)


class List(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAcceptDrops(True)
        self.model = DataModel()
        self.setModel(self.model)

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