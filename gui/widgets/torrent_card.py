from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QMenu
from PySide6.QtCore import Qt, Signal
import libtorrent as lt

class TorrentCard(QWidget):
    action_requested = Signal(object, str)

    def __init__(self, handle, parent=None):
        super().__init__(parent)
        self.handle = handle
        self.setMinimumHeight(80)
        self.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
            QLabel { background: transparent; color: #e0e0e0; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.name_label = QLabel("Loading...")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #2c2c3a;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 4px;
            }
        """)
        
        self.status_label = QLabel("...")
        self.status_label.setStyleSheet("font-size: 11px; color: #aaaaaa;")
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)
        
    def update_status(self, status):
        self.name_label.setText(status['name'] or "Loading...")
        self.progress.setValue(int(status['progress']))
        
        dl_kb = status['download_rate'] / 1024
        ul_kb = status['upload_rate'] / 1024
        peers = status['num_peers']
        state = status['state']
        self.status_label.setText(f"{state.capitalize()} | {peers} Peers | DL: {dl_kb:.1f} KB/s | UL: {ul_kb:.1f} KB/s")

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #2c2c3a; color: white; border: 1px solid #444; } QMenu::item:selected { background-color: #4a90e2; }")
        
        pause_action = menu.addAction("Pause")
        resume_action = menu.addAction("Resume")
        menu.addSeparator()
        remove_action = menu.addAction("Remove")
        remove_data_action = menu.addAction("Remove and Delete Data")
        
        action = menu.exec(event.globalPos())
        
        if action == pause_action:
            self.action_requested.emit(self.handle, "pause")
        elif action == resume_action:
            self.action_requested.emit(self.handle, "resume")
        elif action == remove_action:
            self.action_requested.emit(self.handle, "remove")
        elif action == remove_data_action:
            self.action_requested.emit(self.handle, "remove_data")
