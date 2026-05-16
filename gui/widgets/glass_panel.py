from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class GlassPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassPanel")
        self.setFixedSize(300, 500)  # example sidebar size
        # Background blur image (pre‑blurred with any image editor)
        self.bg_label = QLabel(self)
        pixmap = QPixmap("resources/background_blur.jpg")
        self.bg_label.setPixmap(pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.bg_label.lower()
        self.setStyleSheet("background: transparent;")  # let the label show through

    def resizeEvent(self, event):
        self.bg_label.resize(self.size())
        super().resizeEvent(event)
