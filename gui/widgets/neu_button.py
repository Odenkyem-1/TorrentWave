from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtCore import Qt, QRectF

class NeuButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(120, 40)
        self.setStyleSheet("border: none; font-weight: bold; color: #e0e0e0;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Background
        bg_color = QColor("#2c2c3a")
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, 12, 12)

        # Shadows (dark outside top‑left, light outside bottom‑right)
        shadow_dark = QColor(0, 0, 0, 80)
        shadow_light = QColor(255, 255, 255, 20)

        # Draw two offset rounded rects
        painter.setBrush(Qt.NoBrush)
        pen_dark = QPen(shadow_dark, 4)
        pen_dark.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen_dark)
        painter.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), 12, 12)

        pen_light = QPen(shadow_light, 4)
        pen_light.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen_light)
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 12, 12)

        # Text
        painter.setPen(QColor("#e0e0e0"))
        painter.drawText(rect, Qt.AlignCenter, self.text())
        painter.end()
