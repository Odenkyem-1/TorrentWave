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
        self.app_data_dir = Path.home() / ".torrentwave"
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        self.load_resume_data()

    def load_resume_data(self):
        for resume_file in self.app_data_dir.glob("*.resume"):
            try:
                with open(resume_file, "rb") as f:
                    data = f.read()
                params = lt.read_resume_data(data)
                handle = self.session.add_torrent(params)
                self.handles[handle] = {'handle': handle, 'save_path': params.save_path, 'name': ''}
            except Exception as e:
                print(f"Failed to load resume data {resume_file}: {e}")

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

    def pause_torrent(self, handle):
        if handle.is_valid():
            handle.pause()

    def resume_torrent(self, handle):
        if handle.is_valid():
            handle.resume()

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
        self.session.pause()
        for h in self.handles:
            if h.is_valid() and h.status().has_metadata:
                h.save_resume_data(lt.resume_data_flags_t.save_info_dict)
        
        # Process alerts to actually save the files before exiting
        end_time = time.time() + 2.0
        while time.time() < end_time:
            self.tick()
            time.sleep(0.1)

    def tick(self):
        """Call this periodically (e.g., via QTimer) to process alerts."""
        alerts = self.session.pop_alerts()
        for a in alerts:
            if a.category() & lt.alert.category_t.error_notification:
                print(f"[Libtorrent Error] {a.message()}")
            elif isinstance(a, lt.save_resume_data_alert):
                try:
                    data = lt.bencode(lt.write_resume_data(a.params))
                    info_hash = str(a.handle.info_hash())
                    filepath = self.app_data_dir / f"{info_hash}.resume"
                    with open(filepath, "wb") as f:
                        f.write(data)
                except Exception as e:
                    print(f"Failed to save resume data: {e}")
