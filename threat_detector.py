from collections import defaultdict, deque
from time import time
from config import LARGE_FILE_BYTES, BULK_FILE_COUNT, BULK_WINDOW_SECONDS, BULK_TOTAL_BYTES

history = defaultdict(deque)

def evaluate(mountpoint, event_type, size_bytes):
    size_bytes = int(size_bytes or 0)

    if event_type in ("created", "moved"):
        now = time()
        q = history[mountpoint]
        q.append((now, size_bytes))

        while q and now - q[0][0] > BULK_WINDOW_SECONDS:
            q.popleft()

        count = len(q)
        total = sum(x[1] for x in q)

        if count >= BULK_FILE_COUNT:
            return "HIGH", f"Bulk activity: {count} files in {BULK_WINDOW_SECONDS}s"
        if total >= BULK_TOTAL_BYTES:
            return "HIGH", f"Bulk volume: {total/(1024**2):.1f} MB in {BULK_WINDOW_SECONDS}s"

    if size_bytes >= LARGE_FILE_BYTES:
        return "MEDIUM", f"Large file: {size_bytes/(1024**2):.1f} MB"
    if event_type == "deleted":
        return "LOW", "File deleted from monitored volume"

    return "LOW", "Normal file activity"

def clear_volume(mountpoint):
    history.pop(mountpoint, None)
