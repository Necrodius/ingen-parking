# app.py
# Initializes Flask, registers blueprints, and starts the background
# scheduler that auto‑updates reservation statuses every 60 s.

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
        supports_credentials=True
    )

    # ── APScheduler (runs inside this process) ────────────────────
    scheduler = BackgroundScheduler(daemon=True, timezone="UTC")

    def update_status_job() -> None:
        """Run the status updater inside an app context."""
        with app.app_context():
            update_reservation_statuses()

    scheduler.add_job(
        update_status_job,
        trigger="interval",
        seconds=60,
        id="reservation_status_updater",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()

    # ── Blueprints ────────────────────────────────────────────────
    app.register_blueprint(auth_bp,              url_prefix="/api/auth")
    app.register_blueprint(user_bp,              url_prefix="/api/users")
    app.register_blueprint(parking_location_bp,  url_prefix="/api/parking_location")
    app.register_blueprint(parking_slot_bp,      url_prefix="/api/parking_slot")
    app.register_blueprint(reservation_bp,       url_prefix="/api/reservation")
    app.register_blueprint(reports_bp,           url_prefix="/api/reports")

    # Health check
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()
