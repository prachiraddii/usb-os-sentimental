# USB Sentinel — macOS OS Security Prototype

## What is actually implemented?
- Detects mounted external volumes under macOS `/Volumes`
- Uses `diskutil` to obtain volume metadata
- Watches each mounted volume using `watchdog`
- Logs create/modify/delete/move events
- Detects large files and bulk activity
- Stores events in SQLite
- Serves live data through Flask REST API
- Frontend polls the API every second

## Setup

```bash
cd USB-Sentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 backend/main.py
```

Then open `frontend/index.html`.

## Real USB test

Connect a USB and wait about one second.

Create a test folder and 25 files:

```bash
mkdir -p "/Volumes/YOUR_USB_NAME/USB_SENTINEL_TEST"
for i in {1..25}; do
  echo "test $i" > "/Volumes/YOUR_USB_NAME/USB_SENTINEL_TEST/file_$i.txt"
done
```

Create a 120 MB file:

```bash
mkfile 120m "/Volumes/YOUR_USB_NAME/USB_SENTINEL_TEST/large_test.bin"
```

## Viva explanation

Physical USB → macOS mount layer → `/Volumes` scanner → Python file monitor → threat detector → SQLite → Flask API → dashboard.

### Important limitation
This prototype reliably detects filesystem changes written to the USB volume. Detecting reads/copies FROM the USB and attributing them to a process requires deeper macOS security APIs such as Endpoint Security. Do not claim basic watchdog monitoring sees every read operation.

The Detection Test button is only a clearly labelled presentation shortcut; the real detector is the Python OS monitoring layer.
