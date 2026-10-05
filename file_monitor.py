from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database import add_event
from threat_detector import evaluate

class USBFileHandler(FileSystemEventHandler):
    def __init__(self, device_name, mountpoint):
        self.device_name = device_name
        self.mountpoint = Path(mountpoint)

    def size(self, path):
        try:
            return Path(path).stat().st_size
        except (FileNotFoundError, PermissionError, OSError):
            return 0

    def handle(self, event_type, src_path, size=0):
        path = Path(src_path)
        if path.is_dir():
            return
        try:
            relative = str(path.relative_to(self.mountpoint))
        except ValueError:
            relative = path.name

        risk, reason = evaluate(str(self.mountpoint), event_type, size)
        add_event(self.device_name, str(self.mountpoint), event_type,
                  relative, size, risk, reason)

    def on_created(self, event):
        if not event.is_directory:
            self.handle("created", event.src_path, self.size(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self.handle("modified", event.src_path, self.size(event.src_path))

    def on_deleted(self, event):
        if not event.is_directory:
            self.handle("deleted", event.src_path, 0)

    def on_moved(self, event):
        if not event.is_directory:
            self.handle("moved", event.dest_path, self.size(event.dest_path))

class FileMonitor:
    def __init__(self):
        self.observers = {}

    def start(self, device_name, mountpoint):
        mountpoint = str(mountpoint)
        if mountpoint in self.observers:
            return
        observer = Observer()
        observer.schedule(USBFileHandler(device_name, mountpoint),
                          mountpoint, recursive=True)
        observer.start()
        self.observers[mountpoint] = observer

    def stop(self, mountpoint):
        observer = self.observers.pop(str(mountpoint), None)
        if observer:
            observer.stop()
            observer.join(timeout=2)

    def stop_all(self):
        for mountpoint in list(self.observers):
            self.stop(mountpoint)
