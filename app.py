
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

DB = "siteguard.db"


def connect_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id TEXT NOT NULL,
                incident TEXT NOT NULL,
                priority TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                created_at TEXT NOT NULL
            )
        """)


def add_incident(worker, incident, priority, action):
    with connect_db() as db:
        cur = db.execute("""
            INSERT INTO incidents
            (worker_id, incident, priority, action, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            worker, incident, priority, action,
            datetime.now(timezone.utc).isoformat()
        ))
        return cur.lastrowid


def get_incidents():
    with connect_db() as db:
        rows = db.execute(
            "SELECT * FROM incidents ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


@app.route("/")
def home():
    return jsonify({
        "app": "SiteGuard AI",
        "message": "Backend is running",
        "demo_mode": True
    })


@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    items = get_incidents()
    opened = [i for i in items if i["status"] == "Open"]

    high = sum(i["priority"] == "High" for i in opened)
    medium = sum(i["priority"] == "Medium" for i in opened)

    score = min(100, 10 + high * 20 + medium * 10)

    return jsonify({
        "workers": 48,
        "open_incidents": len(opened),
        "risk_score": score,
        "risk_level": (
            "HIGH" if score >= 60 else
            "MEDIUM" if score >= 30 else "LOW"
        ),
        "incidents": items
    })


@app.route("/api/incidents", methods=["GET"])
def list_incidents():
    return jsonify(get_incidents())


@app.route("/api/incidents", methods=["POST"])
def create_incident():
    data = request.get_json(silent=True) or {}

    worker = data.get("worker_id", "W-104")
    incident = data.get("incident")
    priority = data.get("priority", "Medium")
    action = data.get("action", "Supervisor review required.")

    if not isinstance(incident, str) or not incident.strip():
        return jsonify({"error": "Incident name is required"}), 400

    if priority not in ["Low", "Medium", "High"]:
        return jsonify({"error": "Invalid priority"}), 400

    new_id = add_incident(
        str(worker)[:50], incident.strip()[:200],
        priority, str(action)[:500]
    )

    return jsonify({
        "message": "Incident saved",
        "id": new_id
    }), 201


@app.route("/api/incidents/<int:incident_id>/resolve",
           methods=["PATCH"])
def resolve_incident(incident_id):
    with connect_db() as db:
        cur = db.execute("""
            UPDATE incidents SET status = 'Resolved'
            WHERE id = ? AND status = 'Open'
        """, (incident_id,))

    if cur.rowcount == 0:
        return jsonify({
            "error": "Open incident not found"
        }), 404

    return jsonify({"message": "Incident resolved"})


@app.route("/api/ppe/demo", methods=["POST"])
def ppe_demo():
    data = request.get_json(silent=True) or {}
    helmet = data.get("helmet")
    vest = data.get("vest")

    if not isinstance(helmet, bool) or not isinstance(vest, bool):
        return jsonify({
            "error": "Send helmet and vest as true or false"
        }), 400

    missing = []
    if not helmet:
        missing.append("helmet")
    if not vest:
        missing.append("safety vest")

    if missing:
        add_incident(
            data.get("worker_id", "W-104"),
            "PPE violation: " + ", ".join(missing),
            "High",
            "Verify PPE and follow site safety procedures."
        )

    return jsonify({
        "demo_mode": True,
        "helmet": "Detected" if helmet else "Missing",
        "vest": "Detected" if vest else "Missing",
        "violation": bool(missing),
        "message": (
            "Demo result only; no image AI analysis performed."
        )
    })


@app.route("/api/zones/entry", methods=["POST"])
def zone_entry():
    data = request.get_json(silent=True) or {}
    zone = data.get("zone", "Crane Zone")

    if zone not in ["Crane Zone", "Excavation Zone",
                    "Restricted Zone"]:
        return jsonify({"error": "Unknown zone"}), 400

    new_id = add_incident(
        data.get("worker_id", "W-104"),
        "Restricted-zone entry: " + zone,
        "High",
        "Verify worker safety and clear the restricted zone."
    )

    return jsonify({
        "message": "Zone incident saved",
        "incident_id": new_id,
        "zone": zone
    }), 201


@app.route("/api/sos", methods=["POST"])
def trigger_sos():
    data = request.get_json(silent=True) or {}

    new_id = add_incident(
        data.get("worker_id", "W-104"),
        "Worker Emergency SOS",
        "High",
        "Contact worker and follow emergency procedures."
    )

    return jsonify({
        "message": "SOS recorded in database",
        "incident_id": new_id,
        "location": data.get("location", "Unknown"),
        "notice": "Demo only; no real person was notified."
    }), 201


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
