from flask import Flask, jsonify
from app.config import Config
from app.models import db
from app.extensions import redis_client, limiter
from app.auth import verify_api_key, auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.before_request(verify_api_key)
    db.init_app(app)
    limiter.init_app(app)

    # basically for 429 error flask is registering this function and returns its output
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Too many requests, slow down"}), 429

    from app.routes.shortener import shortener_bp
    from app.routes.analytics import analytics_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(shortener_bp)
    app.register_blueprint(analytics_bp)

    return app