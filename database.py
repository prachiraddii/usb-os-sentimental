import sqlite3
from datetime import datetime, timezone
from config import DB_PATH

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            device TEXT NOT NULL,
            mountpoint TEXT NOT NULL,
            event_type TEXT NOT NULL,
            path TEXT NOT NULL,
            size_bytes INTEGER DEFAULT 0,
            risk TEXT NOT NULL,
            details TEXT
        )""")
        conn.commit()

def add_event(device, mountpoint, event_type, path, size_bytes, risk, details):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """INSERT INTO events
            (timestamp,device,mountpoint,event_type,path,size_bytes,risk,details)
            VALUES (?,?,?,?,?,?,?,?)""",
            (now_iso(), device, mountpoint, event_type, path,
             int(size_bytes or 0), risk, details)
        )
        conn.commit()
        return cur.lastrowid

def get_events(limit=100):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()]

def clear_events():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM events")
        conn.commit()
