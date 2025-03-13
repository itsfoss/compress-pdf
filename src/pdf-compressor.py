import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QFileDialog, QGridLayout, QRadioButton, QToolButton,
                             QFrame, QSizePolicy, QLineEdit, QVBoxLayout, QHBoxLayout, QButtonGroup)
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QColor, QFont
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMessageBox
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtCore import QMetaObject, Qt
import humanize

if getattr(sys, 'frozen', False):
    app_dir = sys._MEIPASS  # PyInstaller's temp folder
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))

class WorkerThread(QThread):
    finished = pyqtSignal(float)  # Signal to indicate when compression is done

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        import time  # Import time inside the thread to avoid any issues
        start_time = time.time()
        
        try:
            subprocess.run(self.command, check=True)
        except subprocess.CalledProcessError:
            self.finished.emit(-1)  # Emit -1 if compression fails
            return
        
        elapsed_time = round(time.time() - start_time, 2)
        self.finished.emit(elapsed_time)  # Emit the time taken for compression


class PdfCompressor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def compressPdf(self):
        print("Compressing PDF...")  # Debugging print statement

    def initUI(self):
        self.setWindowTitle("Compress PDF by It's FOSS")
        self.resize(700, 450)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #F8F9FA; font-family: 'Poppins'; border-radius: 10px;")
        self.pdf_icon_label = QLabel()
        self.pdf_icon_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.or_label = QLabel("OR")
        self.select_button = QPushButton("Select PDF")
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.pdf_icon_label)
        self.left_layout.addWidget(self.or_label)
        self.left_layout.addWidget(self.select_button)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)         

        # Placeholder for Logo
        self.logo_label = QLabel()
        self.logo_label.setFixedHeight(35)
        self.logo_label.setPixmap(QPixmap(os.path.join(app_dir, "assets/itsfoss-logo.webp")))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Left Panel - Drag and Drop Area
        self.pdf_icon_label = QLabel()
        self.pdf_icon_label.setPixmap(QPixmap("arc_pdf_icon.png").scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
        self.pdf_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_icon_label.setStyleSheet("border: 4px dashed #bcbcbc; padding: 0px; border-radius: 10px;")
        self.pdf_icon_label.setText("Drag & Drop a PDF Here")
        self.pdf_icon_label.setFont(QFont("Poppins", 10, QFont.Weight.Bold))
        self.pdf_icon_label.setFixedSize(260, 180)

        self.or_label = QLabel("OR")
        self.or_label.setFont(QFont("Poppins", 10, QFont.Weight.Bold))
        self.or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.select_button = QPushButton("Select PDF")
        self.select_button.setStyleSheet("background-color: #8fce00; color: white; padding: 8px; border-radius: 5px;")
        self.select_button.clicked.connect(self.selectFile)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.pdf_icon_label)
        left_layout.addWidget(self.or_label)
        left_layout.addWidget(self.select_button)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Right Panel - Compression Levels
        self.high_radio = QRadioButton("High")
        self.high_radio.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        self.high_radio.setStyleSheet("color: #8fce00;")
        self.high_sub_label = QLabel("Best quality, larger file size")
        self.high_sub_label.setStyleSheet("font-size: 12px; color: #5b5b5b;")

        self.medium_radio = QRadioButton("Medium")
        self.medium_radio.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        self.medium_radio.setStyleSheet("color: #8fce00;")
        self.medium_sub_label = QLabel("Balanced quality and file size")
        self.medium_sub_label.setStyleSheet("font-size: 12px; color: #5b5b5b;")

        self.low_radio = QRadioButton("Low")
        self.low_radio.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        self.low_radio.setStyleSheet("color: #8fce00;")
        self.low_sub_label = QLabel("Smallest file size, reduced quality")
        self.low_sub_label.setStyleSheet("font-size: 12px; color: #5b5b5b;")

        
        # Ensuring only one button is selected at a time
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.high_radio)
        self.radio_group.addButton(self.medium_radio)
        self.radio_group.addButton(self.low_radio)
        self.medium_radio.setChecked(True)

        right_layout = QVBoxLayout()
        for radio, sub_label in [(self.high_radio, self.high_sub_label),
                                (self.medium_radio, self.medium_sub_label),
                                (self.low_radio, self.low_sub_label)]:
            row_layout = QVBoxLayout()
            row_layout.addWidget(radio)
            row_layout.addWidget(sub_label)
            right_layout.addLayout(row_layout)
            right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("border: 2px solid #CCCCCC;")
        
        # Main Layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addWidget(separator)
        main_layout.addLayout(right_layout)

        # Horizontal Separator
        horizontal_separator = QFrame()
        horizontal_separator.setFrameShape(QFrame.Shape.HLine)
        horizontal_separator.setStyleSheet("border: 2px solid #CCCCCC;")

        # Output Folder Section
        self.output_label = QLabel("Output Folder :")
        self.output_label.setFont(QFont("Poppins", 10, QFont.Weight.Bold))
        self.output_path = QLineEdit(os.path.expanduser("~/Desktop"))
        self.output_path.setStyleSheet("border: 1px solid #CCCCCC; padding: 5px; border-radius: 5px;")
        self.output_button = QPushButton("...")
        self.output_button.setFixedSize(30, 30)
        self.output_button.setStyleSheet("border: 1px solid #0078D4; border-radius: 5px;")
        self.output_button.clicked.connect(self.selectOutputFolder)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.output_button)
        output_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Buttons Section
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("border: 1px solid #CCCCCC; border-radius: 5px; padding: 10px;")
        self.compress_button = QPushButton("Compress")
        self.compress_button.setStyleSheet("background-color: #8fce00; color: white; padding: 10px; border-radius: 5px;")
        self.compress_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.clicked.connect(self.close)
        self.compress_button.clicked.connect(self.compressPdf)
        self.compress_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.output_label)
        button_layout.addWidget(self.output_path)
        button_layout.addWidget(self.output_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.compress_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Final Layout
        final_layout = QVBoxLayout()
        final_layout.addWidget(self.logo_label)
        final_layout.addSpacing(20)
        final_layout.addLayout(main_layout)
        final_layout.addSpacing(10)
        final_layout.addWidget(horizontal_separator)
        final_layout.addLayout(button_layout)
        final_layout.addSpacing(10)
        
        self.setLayout(final_layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].lower().endswith('.pdf'):
            self.selected_file = files[0]
            self.displayPdfInfo()
            self.compress_button.setEnabled(True)

    def displayPdfInfo(self):
        if self.selected_file:
            file_name = os.path.basename(self.selected_file)

            # ✅ Get file size in MB and format it nicely
            file_size = os.path.getsize(self.selected_file) / (1024 * 1024)  # Convert to MB
            file_size_text = f"Size: {humanize.naturalsize(file_size, binary=True)}"  # e.g., "2.4 MB"

            # ✅ Construct the correct path for the image
            pdf_icon_path = os.path.join(app_dir, "assets", "pdf.png")

            # ✅ Load the image from the correct path
            pixmap = QPixmap(pdf_icon_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)

            # ✅ Apply the image to the label
            self.pdf_icon_label.setStyleSheet("border: 2px solid #0078D4; padding: 10px; border-radius: 10px;")
            self.pdf_icon_label.setPixmap(pixmap)

            # Hide original widgets
            self.or_label.hide()
            self.select_button.hide()

            # ✅ Clear existing layout
            if self.pdf_icon_label.layout():
                old_layout = self.pdf_icon_label.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                del old_layout

            # ✅ Create a vertical layout for file info
            layout = QVBoxLayout()
            layout.setContentsMargins(5, 0, 0, 0)

            # ✅ PDF Icon
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setStyleSheet("QLabel {border: none;}")
            layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

            # ✅ PDF Name Label (Multi-line, Centered)
            file_label = QLabel(file_name)
            file_label.setStyleSheet("font-weight: bold;")
            file_label.setWordWrap(True)  # ✅ Enable text wrapping
            file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(file_label)

            # ✅ PDF Size Label (Dark Gray, Bold)
            size_label = QLabel(file_size_text)
            size_label.setStyleSheet("color: #5b5b5b; font-size: 12px; font-weight: bold;")
            size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(size_label)

            # ✅ Apply the new layout
            self.pdf_icon_label.setLayout(layout)
            self.pdf_icon_label.setStyleSheet("border: none;")
        else:
            # Reset if no file is selected
            self.pdf_icon_label.setText("Drag & Drop a PDF Here")
            self.pdf_icon_label.setStyleSheet("border: 4px dashed #CCCCCC; padding: 30px; border-radius: 10px;")
            self.pdf_icon_label.setPixmap(QPixmap("arc_pdf_icon.png").scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            self.pdf_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.or_label.show()
            self.select_button.show()

    def selectFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_name:
            self.selected_file = file_name
            self.displayPdfInfo()
            self.compress_button.setEnabled(True)

    def selectOutputFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path.setText(folder)

    def compressPdf(self):
        if not self.selected_file:
            return

        filename = os.path.splitext(os.path.basename(self.selected_file))[0]
        output_filename = f"compressed-{filename}.pdf"
        
        output_folder = self.output_path.text().strip()
        if not output_folder:
            output_folder = os.path.expanduser("~/Desktop")

        output_file = os.path.join(output_folder, output_filename)

        command = ["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", "-dPDFSETTINGS=/screen",
                   "-dNOPAUSE", "-dBATCH", f"-sOutputFile={output_file}", self.selected_file]

        # ✅ Show "Compressing..." message box
        self.message_box = QMessageBox(self)
        self.message_box.setIcon(QMessageBox.Icon.Information)
        self.message_box.setWindowTitle("Compression in Progress")
        self.message_box.setText("Compressing your PDF... Hang tight! 🚀")
        self.message_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
        self.message_box.show()

        # ✅ Start the Worker Thread for Compression
        self.worker = WorkerThread(command)
        self.worker.finished.connect(self.compressionFinished)  # ✅ Fix: This function must exist!
        self.worker.start()  # Start the background compression

    def compressionFinished(self, elapsed_time):  # ✅ Fix: This function must exist!
        if hasattr(self, 'message_box') and self.message_box is not None:
            QMetaObject.invokeMethod(self.message_box, "accept", Qt.ConnectionType.QueuedConnection)

        if elapsed_time == -1:
            QMessageBox.critical(self, "Error", "Compression failed. Make sure Ghostscript is installed.")
        else:
            QMessageBox.information(self, "Compression Complete", f"PDF compressed successfully in {elapsed_time} seconds!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfCompressor()
    window.show()
    sys.exit(app.exec())
