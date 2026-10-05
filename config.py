from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "usb_sentinel.db"
VOLUMES_DIR = Path("/Volumes")

LARGE_FILE_BYTES = 100 * 1024 * 1024
BULK_FILE_COUNT = 20
BULK_WINDOW_SECONDS = 30
BULK_TOTAL_BYTES = 500 * 1024 * 1024
SCAN_INTERVAL_SECONDS = 1
MAX_EVENTS = 100
