import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                                QHBoxLayout, QWidget, QListWidget, QListWidgetItem,
                                QLabel, QProgressBar, QPushButton, QFileDialog)
from PySide6.QtCore import QTimer, Qt, QSize
from core.engine import TorrentManager
from gui.widgets.glass_panel import GlassPanel
from gui.widgets.neu_button import NeuButton
from gui.widgets.torrent_card import TorrentCard
from gui.widgets.file_tree import FileTree

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
        
        self.file_tree = FileTree()
        detail_layout.addWidget(self.file_tree)

        main_layout.addWidget(self.detail_card)
        
        # Connect selection changed
        self.torrent_list.currentItemChanged.connect(self.on_selection_changed)

        # Timer to update UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

        # Set stylesheet
        with open("gui/styles/theme.qss", "r") as f:
            self.setStyleSheet(f.read())

        # Populate list with already loaded handles
        for handle in self.engine.handles:
            self._add_list_item(handle)

    def add_torrent_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Torrent File", "",
                                                   "Torrent Files (*.torrent);;All Files (*)")
        if file_path:
            save_dir = QFileDialog.getExistingDirectory(self, "Choose Save Location",
                                                         self.engine.default_save_path)
            handle = self.engine.add_torrent(file_path, save_dir)
            self._add_list_item(handle)

    def _add_list_item(self, handle):
        item = QListWidgetItem()
        item.setSizeHint(QSize(280, 80))
        self.torrent_list.addItem(item)
        
        card = TorrentCard(handle)
        card.action_requested.connect(self.handle_torrent_action)
        self.torrent_list.setItemWidget(item, card)
        self.torrent_items[item] = handle

    def handle_torrent_action(self, handle, action):
        if action == "pause":
            self.engine.pause_torrent(handle)
        elif action == "resume":
            self.engine.resume_torrent(handle)
        elif action in ("remove", "remove_data"):
            delete_files = (action == "remove_data")
            self.engine.remove_torrent(handle, delete_files)
            
            # Remove from UI
            for item, h in list(self.torrent_items.items()):
                if h == handle:
                    row = self.torrent_list.row(item)
                    self.torrent_list.takeItem(row)
                    del self.torrent_items[item]
                    break
            
            if self.file_tree.current_handle == handle:
                self.file_tree.clear()
                self.file_tree.current_handle = None

    def on_selection_changed(self, current, previous):
        if current in self.torrent_items:
            self.file_tree.set_torrent(self.torrent_items[current])

    def update_ui(self):
        self.engine.tick()
        # Update all list items
        for item, handle in self.torrent_items.items():
            status = self.engine.get_status(handle)
            card = self.torrent_list.itemWidget(item)
            if card: card.update_status(status)
            
        # Update file tree
        self.file_tree.update_files()

    def closeEvent(self, event):
        self.timer.stop()
        self.engine.save_resume_data()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
