from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtCore import Qt

class FileTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["File", "Size", "Progress", "Priority"])
        self.setStyleSheet("""
            QTreeWidget { background: transparent; color: #e0e0e0; border: none; font-size: 13px; }
            QHeaderView::section { background-color: #1a1a2e; color: white; border: none; padding: 4px; font-weight: bold; }
        """)
        self.current_handle = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_torrent(self, handle):
        self.current_handle = handle
        self.clear()
        self.update_files()

    def update_files(self):
        if not self.current_handle or not self.current_handle.is_valid():
            return
            
        ti = self.current_handle.torrent_file()
        if not ti:
            return  # Metadata not downloaded yet
            
        file_progress = self.current_handle.file_progress()
        priorities = self.current_handle.file_priorities()
        num_files = ti.num_files()
        
        # If UI tree is empty, populate it
        if self.topLevelItemCount() == 0:
            for i in range(num_files):
                size = ti.files().file_size(i)
                name = ti.files().file_name(i)
                item = QTreeWidgetItem([name, f"{size/1024/1024:.2f} MB", "0%", "Normal"])
                item.setData(0, Qt.UserRole, i) # Store index
                self.addTopLevelItem(item)
                
        # Update progress and priority
        for i in range(num_files):
            item = self.topLevelItem(i)
            if not item: continue
            size = ti.files().file_size(i)
            prog = (file_progress[i] / size * 100) if size > 0 else 100
            item.setText(2, f"{prog:.1f}%")
            
            prio = "Normal"
            if len(priorities) > i:
                if priorities[i] == 0: prio = "Skip"
                elif priorities[i] == 7: prio = "High"
            item.setText(3, prio)

    def show_context_menu(self, pos):
        if not self.current_handle:
            return
        item = self.itemAt(pos)
        if not item: return
        
        file_idx = item.data(0, Qt.UserRole)
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #2c2c3a; color: white; border: 1px solid #444; } QMenu::item:selected { background-color: #4a90e2; }")
        
        norm_act = menu.addAction("Priority: Normal")
        high_act = menu.addAction("Priority: High")
        skip_act = menu.addAction("Skip (Don't Download)")
        
        action = menu.exec(self.viewport().mapToGlobal(pos))
        
        if action == norm_act:
            self.current_handle.file_priority(file_idx, 4)
        elif action == high_act:
            self.current_handle.file_priority(file_idx, 7)
        elif action == skip_act:
            self.current_handle.file_priority(file_idx, 0)
        self.update_files()
