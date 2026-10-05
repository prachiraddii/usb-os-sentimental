import plistlib
import subprocess
import threading
import time
from pathlib import Path
from config import VOLUMES_DIR, SCAN_INTERVAL_SECONDS
from database import add_event
from file_monitor import FileMonitor
from threat_detector import clear_volume

class USBMonitor:
    def __init__(self):
        self.file_monitor = FileMonitor()
        self.devices = {}
        self.lock = threading.Lock()
        self.running = False

    def disk_info(self, mountpoint):
        try:
            r = subprocess.run(
                ["diskutil", "info", "-plist", str(mountpoint)],
                capture_output=True, timeout=3
            )
            if r.returncode == 0 and r.stdout:
                return plistlib.loads(r.stdout)
        except Exception:
            pass
        return {}

    def scan_mounts(self):
        mounts = {}
        if not VOLUMES_DIR.exists():
            return mounts

        for path in VOLUMES_DIR.iterdir():
            if not path.is_dir():
                continue
            info = self.disk_info(path)
            mounts[str(path)] = {
                "name": info.get("VolumeName") or path.name,
                "device_id": info.get("DeviceIdentifier") or "unknown",
                "protocol": info.get("BusProtocol") or info.get("Protocol") or "Unknown"
            }
        return mounts

    def scan_once(self):
        current = self.scan_mounts()
        with self.lock:
            old = set(self.devices)
        new = set(current)

        for mountpoint in sorted(new - old):
            d = current[mountpoint]
            device = {
                "name": d["name"],
                "mountpoint": mountpoint,
                "device_id": d["device_id"],
                "protocol": d["protocol"],
                "connected_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with self.lock:
                self.devices[mountpoint] = device

            add_event(d["name"], mountpoint, "device_connected", "-",
                      0, "LOW", f"Mounted volume detected ({d['protocol']})")
            try:
                self.file_monitor.start(d["name"], mountpoint)
            except Exception as exc:
                add_event(d["name"], mountpoint, "monitor_error", "-",
                          0, "HIGH", str(exc))

        for mountpoint in sorted(old - new):
            with self.lock:
                device = self.devices.pop(mountpoint, None)
            if device:
                self.file_monitor.stop(mountpoint)
                clear_volume(mountpoint)
                add_event(device["name"], mountpoint, "device_disconnected",
                          "-", 0, "LOW", "Mounted volume removed")

    def loop(self):
        while self.running:
            try:
                self.scan_once()
            except Exception as exc:
                print("Monitor error:", exc)
            time.sleep(SCAN_INTERVAL_SECONDS)

    def start(self):
        if self.running:
            return
        self.running = True
        self.scan_once()
        threading.Thread(target=self.loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.file_monitor.stop_all()

    def get_devices(self):
        with self.lock:
            return list(self.devices.values())
