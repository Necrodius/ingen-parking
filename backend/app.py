# Initializes Flask, registers blueprints, and starts the background
# scheduler that auto‑updates reservation statuses every 60 s.

import os
import sys
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify
from config import Config
from extensions import db, jwt, cors

# Blueprints
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.parking_location_routes import parking_location_bp
from routes.parking_slot_routes import parking_slot_bp
from routes.reservation_routes import reservation_bp
from routes.reports_routes import reports_bp

# Scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from tasks.status_scheduler import update_reservation_statuses


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Extensions ────────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}},
        supports_credentials=True,
    )

    # ── APScheduler ───────────────────────────────────────────────
    scheduler = BackgroundScheduler(daemon=True, timezone="UTC")

    def update_status_job() -> None:
        """Run the status updater inside an app context."""
        with app.app_context():
            now = datetime.now(timezone.utc)
            app.logger.info(
                "🕒 Triggering reservation status update at %s", now.isoformat()
            )
            update_reservation_statuses()

    scheduler.add_job(
        update_status_job,
        trigger="interval",
        seconds=30,          # set to 5 for quick local testing
        id="reservation_status_updater",
        max_instances=1,
        replace_existing=True,
    )

    # Start the scheduler once (works with Gunicorn preload & Flask reload)
    if not app.debug:
        scheduler.start()
        app.logger.info("✅ APScheduler started. Jobs: %s", scheduler.get_jobs())

    # ── Blueprints ────────────────────────────────────────────────
    app.register_blueprint(auth_bp,             url_prefix="/api/auth")
    app.register_blueprint(user_bp,             url_prefix="/api/users")
    app.register_blueprint(parking_location_bp, url_prefix="/api/parking_location")
    app.register_blueprint(parking_slot_bp,     url_prefix="/api/parking_slot")
    app.register_blueprint(reservation_bp,      url_prefix="/api/reservation")
    app.register_blueprint(reports_bp,          url_prefix="/api/reports")

    # Health check
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # ── Logging: send app.logger to STDOUT so Docker/Gunicorn capture it ──
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(process)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    if not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    return app


app = create_app()
