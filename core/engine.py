import libtorrent as lt
import time
import os
from pathlib import Path

class TorrentManager:
    def __init__(self):
        self.session = lt.session()
        settings = self.session.get_settings()
        settings['enable_dht'] = True
        settings['enable_lsd'] = True
        settings['enable_upnp'] = True
        settings['enable_natpmp'] = True
        settings['active_downloads'] = 8
        settings['active_seeds'] = 4
        self.session.apply_settings(settings)

        self.handles = {}          # torrent_handle -> info dict
        self.default_save_path = str(Path.home() / "Downloads")

    def add_torrent(self, uri_or_path, save_path=None):
        """Add from .torrent file or magnet URI."""
        if save_path is None:
            save_path = self.default_save_path

        params = lt.parse_magnet_uri(uri_or_path) if uri_or_path.startswith('magnet:') else {'ti': lt.torrent_info(uri_or_path)}
        params['save_path'] = save_path
        handle = self.session.add_torrent(params)
        info = {'handle': handle, 'save_path': save_path, 'name': ''}
        self.handles[handle] = info
        return handle

    def remove_torrent(self, handle, delete_files=False):
        if handle in self.handles:
            self.session.remove_torrent(handle, 1 if delete_files else 0)
            del self.handles[handle]

    def get_status(self, handle):
        s = handle.status()
        return {
            'name': s.name,
            'progress': s.progress * 100,
            'download_rate': s.download_rate,
            'upload_rate': s.upload_rate,
            'num_peers': s.num_peers,
            'state': str(s.state),
            'total_size': s.total_wanted,
            'total_done': s.total_wanted_done,
            'save_path': self.handles.get(handle, {}).get('save_path', ''),
        }

    def set_speed_limit(self, handle, download_limit=-1, upload_limit=-1):
        handle.set_download_limit(download_limit)   # bytes/s, -1 = unlimited
        handle.set_upload_limit(upload_limit)

    def set_global_limits(self, dl_limit, ul_limit):
        settings = self.session.get_settings()
        settings['download_rate_limit'] = dl_limit
        settings['upload_rate_limit'] = ul_limit
        self.session.apply_settings(settings)

    def save_resume_data(self):
        for h in self.handles:
            h.save_resume_data()
        # later you can load resume files via session.add_torrent() with resume_data

    def tick(self):
        """Call this periodically (e.g., via QTimer) to process alerts."""
        alerts = self.session.pop_alerts()
        for a in alerts:
            if a.category() & lt.alert.category_t.error_notification:
                print(f"[Libtorrent Error] {a.message()}")
