from flask import Flask
from app.config import Config
from app.models import db
from app.extensions import redis_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from app.routes.shortener import shortener_bp
    from app.routes.analytics import analytics_bp
    app.register_blueprint(shortener_bp)
    app.register_blueprint(analytics_bp)

    return app