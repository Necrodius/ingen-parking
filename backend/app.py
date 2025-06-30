# This file initializes the Flask application and sets up core services like the database and JWT.
# It also registers all the API blueprints (routes) and defines a health check endpoint.

from flask import Flask, jsonify
from config import Config
from extensions import db, jwt
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.parking_location_routes import parking_location_bp
from routes.parking_slot_routes import parking_slot_bp
from routes.reservation_routes import reservation_bp
from routes.reports_routes import reports_bp

def create_app() -> Flask:
    app = Flask(__name__)
    
    # Load app settings from config.py
    app.config.from_object(Config)

    # Initialize extensions (SQLAlchemy and JWT)
    db.init_app(app)
    jwt.init_app(app)

    # Register API route blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(parking_location_bp, url_prefix="/api/parking_location")
    app.register_blueprint(parking_slot_bp, url_prefix="/api/parking_slot")
    app.register_blueprint(reservation_bp, url_prefix="/api/reservation")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    # Health check endpoint for monitoring
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app

app = create_app()
