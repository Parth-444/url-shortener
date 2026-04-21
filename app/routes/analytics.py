from app.models import db, Click, URL
from flask import jsonify, request
from flask.blueprints import Blueprint
from sqlalchemy import func
from datetime import timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def to_ist(dt):
    """Convert a naive UTC datetime to IST and return ISO format string."""
    return dt.replace(tzinfo=timezone.utc).astimezone(IST).isoformat()

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/stats/<short_code>", methods=["GET"])
def get_stats(short_code):
    url = URL.query.filter_by(short_code=short_code).first()

    if not url:
        return jsonify({"error": "code not mapped yet"}), 404

    total_clicks = db.session.query(func.count(Click.id)).filter(Click.url_id == url.id).scalar()

    # Pagination params
    page     = request.args.get("page", 1, type=int)
    page     = max(1, page)
    per_page = request.args.get("per_page", 7, type=int)
    per_page = min(per_page, 90)  # hard cap
    offset   = (page - 1) * per_page

    # Base query for clicks grouped by day
    cpd_query = (
        db.session.query(func.date(Click.clicked_at), func.count(Click.id))
        .filter(Click.url_id == url.id)
        .group_by(func.date(Click.clicked_at))
        .order_by(func.date(Click.clicked_at).desc())
    )

    total_days       = cpd_query.count()
    total_pages      = max(1, -(-total_days // per_page))  # ceiling division
    clicks_per_day_rows = cpd_query.limit(per_page).offset(offset).all()
    clicks_per_day   = [{"date": str(row[0]), "clicks": row[1]} for row in clicks_per_day_rows]

    last_clicked_query = db.session.query(Click.clicked_at).filter(Click.url_id==url.id).order_by(Click.clicked_at.desc()).first()
    last_clicked = to_ist(last_clicked_query[0]) if last_clicked_query else None

    return jsonify({
        "short_code": url.short_code,
        "total_clicks": total_clicks,
        "last_clicked": last_clicked,
        "clicks_per_day": {
            "page": page,
            "per_page": per_page,
            "total_days": total_days,
            "total_pages": total_pages,
            "data": clicks_per_day
        }
    })