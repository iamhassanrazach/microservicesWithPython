# logging-service — Flask app (not FastAPI — intentional, see docs/specs.md)
#
# Run with:   flask --app app.main run --port 8006
#
# Implements the four GDPR consent endpoints plus a log-listing endpoint
# used for verification. Response shapes follow docs/api-contracts.md.

import os
import threading
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from app.models import ActivityLog, Consent, db

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///./logging.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    # Start the RabbitMQ consumer in a background thread
    from app.consumer import start_consumer
    threading.Thread(target=start_consumer, args=(app,), daemon=True).start()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "logging-service"})


# ---------------------------------------------------------------------------
# Consent lifecycle
# ---------------------------------------------------------------------------

@app.post("/v1/consent/<user_id>")
def set_consent(user_id):
    """
    Record or update a user's GDPR consent decision.
    Request body: { "granted": true }
    """
    body = request.get_json(silent=True) or {}
    granted = bool(body.get("granted", False))

    consent = Consent.query.get(user_id)
    if consent is None:
        consent = Consent(user_id=user_id, granted=granted)
        db.session.add(consent)
    else:
        consent.granted = granted
        consent.updated_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        "user_id": user_id,
        "granted": consent.granted,
        "updated_at": consent.updated_at.isoformat(),
    }), 200


@app.get("/v1/consent/<user_id>")
def get_consent(user_id):
    """Check a user's current consent status."""
    consent = Consent.query.get(user_id)
    if consent is None:
        return jsonify({"detail": "No consent record found"}), 404

    return jsonify({
        "user_id": user_id,
        "granted": consent.granted,
        "updated_at": consent.updated_at.isoformat(),
    }), 200


@app.delete("/v1/consent/<user_id>")
def withdraw_consent(user_id):
    """Withdraw consent — sets granted to False (does not delete the record)."""
    consent = Consent.query.get(user_id)
    if consent is None:
        return jsonify({"detail": "No consent record found"}), 404

    consent.granted = False
    consent.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        "user_id": user_id,
        "granted": consent.granted,
        "updated_at": consent.updated_at.isoformat(),
    }), 200


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------

@app.delete("/v1/logs/<user_id>")
def delete_logs(user_id):
    """GDPR right to erasure — permanently delete all log entries for a user."""
    deleted_count = ActivityLog.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({
        "user_id": user_id,
        "deleted_entries": deleted_count,
    }), 200


@app.get("/v1/logs/<user_id>")
def get_logs(user_id):
    """List all stored log entries for a user (for testing/verification)."""
    logs = ActivityLog.query.filter_by(user_id=user_id).all()

    items = [{
        "id": log.id,
        "user_id": log.user_id,
        "game_id": log.game_id,
        "action": log.action,
        "message": log.message,
        "created_at": log.created_at.isoformat(),
    } for log in logs]

    return jsonify({"items": items, "total": len(items)}), 200
