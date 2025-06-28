# This file initializes the Flask application, and sets up the database connection using SQLAlchemy.
# API endpoints are also defined here.

from flask import Flask, jsonify
import os

from extensions import db
from routes.user_routes import user_bp
from routes.parking_location_routes import parking_location_bp
from routes.parking_slot_routes import parking_slot_bp
from routes.reservation_routes import reservation_bp

def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    app.register_blueprint(user_bp,               url_prefix="/api")
    app.register_blueprint(parking_location_bp,   url_prefix="/api")
    app.register_blueprint(parking_slot_bp,       url_prefix="/api")
    app.register_blueprint(reservation_bp,        url_prefix="/api")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app

app = create_app()
