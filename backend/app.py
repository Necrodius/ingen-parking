from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app

app = create_app()
