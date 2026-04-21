from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class URL(db.Model):
    __tablename__ = "urls"

    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    original_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    clicks = db.relationship("Click", backref="url", lazy=True)

class Click(db.Model):
    __tablename__ = "clicks"

    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey("urls.id"), nullable=False, index=True)
    clicked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    