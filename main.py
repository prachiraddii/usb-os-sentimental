from flask import Flask, jsonify
from flask_cors import CORS
from config import MAX_EVENTS
from database import init_db, get_events, clear_events, add_event
from usb_monitor import USBMonitor

app = Flask(__name__)
CORS(app)
init_db()

monitor = USBMonitor()
monitor.start()

@app.get("/api/state")
def state():
    events = get_events(MAX_EVENTS)
    alerts = [e for e in events if e["risk"] in ("MEDIUM", "HIGH")]
    return jsonify({
        "devices": monitor.get_devices(),
        "events": events,
        "alerts": alerts[:20],
        "stats": {
            "devices": len(monitor.get_devices()),
            "events": len(events),
            "alerts": len(alerts),
            "high_risk": sum(e["risk"] == "HIGH" for e in events),
            "medium_risk": sum(e["risk"] == "MEDIUM" for e in events)
        }
    })

@app.post("/api/scan")
def scan():
    monitor.scan_once()
    return jsonify({"ok": True})

@app.delete("/api/events")
def delete_events():
    clear_events()
    return jsonify({"ok": True})

@app.post("/api/demo/bulk")
def demo_bulk():
    add_event("DEMO-USB", "/Volumes/USB-SENTINEL-DEMO",
              "demo_detection", "demo/bulk_transfer_test",
              600*1024*1024, "HIGH",
              "Demo trigger: simulated bulk transfer for presentation")
    return jsonify({"ok": True})

if __name__ == "__main__":
    print("USB Sentinel: http://127.0.0.1:5000")
    print("Monitoring macOS mounted volumes under /Volumes")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
