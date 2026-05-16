import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                                QHBoxLayout, QWidget, QListWidget, QListWidgetItem,
                                QLabel, QProgressBar, QPushButton, QFileDialog)
from PySide6.QtCore import QTimer, Qt
from core.engine import TorrentManager
from gui.widgets.glass_panel import GlassPanel
from gui.widgets.neu_button import NeuButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TorrentWave")
        self.setMinimumSize(1000, 650)

        self.engine = TorrentManager()
        self.torrent_items = {}  # QListWidgetItem -> torrent_handle

        # --- Layout ---
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Left: glass sidebar
        self.sidebar = GlassPanel()
        sidebar_layout = QVBoxLayout(self.sidebar)
        self.torrent_list = QListWidget()
        self.torrent_list.setStyleSheet("background: transparent; border: none;")
        sidebar_layout.addWidget(QLabel("Torrents", styleSheet="color: white; font-size:16px;"))
        sidebar_layout.addWidget(self.torrent_list)

        add_btn = NeuButton("+ Add")
        add_btn.clicked.connect(self.add_torrent_dialog)
        sidebar_layout.addWidget(add_btn)

        main_layout.addWidget(self.sidebar)

        # Right: detail area (neumorphic card)
        self.detail_card = QWidget()
        self.detail_card.setObjectName("detailCard")
        detail_layout = QVBoxLayout(self.detail_card)
        self.name_label = QLabel("No torrent selected")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.dl_speed_label = QLabel("DL: 0 KB/s")
        detail_layout.addWidget(self.name_label)
        detail_layout.addWidget(self.progress)
        detail_layout.addWidget(self.dl_speed_label)

        main_layout.addWidget(self.detail_card)

        # Timer to update UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

        # Set stylesheet
        with open("gui/styles/theme.qss", "r") as f:
            self.setStyleSheet(f.read())

    def add_torrent_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Torrent File", "",
                                                   "Torrent Files (*.torrent);;All Files (*)")
        if file_path:
            save_dir = QFileDialog.getExistingDirectory(self, "Choose Save Location",
                                                         self.engine.default_save_path)
            handle = self.engine.add_torrent(file_path, save_dir)
            self._add_list_item(handle)

    def _add_list_item(self, handle):
        item = QListWidgetItem(handle.status().name or "Loading...")
        self.torrent_list.addItem(item)
        self.torrent_items[item] = handle

    def update_ui(self):
        self.engine.tick()
        # Update all list items
        for item, handle in self.torrent_items.items():
            status = self.engine.get_status(handle)
            item.setText(f"{status['name']} - {status['progress']:.1f}%")
        # Update selected torrent details
        selected = self.torrent_list.currentItem()
        if selected and selected in self.torrent_items:
            st = self.engine.get_status(self.torrent_items[selected])
            self.name_label.setText(st['name'])
            self.progress.setValue(int(st['progress']))
            self.dl_speed_label.setText(f"DL: {st['download_rate']/1024:.1f} KB/s")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
