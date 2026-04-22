from flask import Blueprint, request, jsonify, redirect
from app.models import URL, Click, db
from app.extensions import redis_client, limiter, get_rate_limit
import random
import string

shortener_bp = Blueprint("shortener", __name__)

def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))

def generate_unique_code():
    """Generate a code that doesn't already exist in the DB."""
    while True:
        code = generate_code()
        if not URL.query.filter_by(short_code=code).first():
            return code


@shortener_bp.route("/shorten", methods=["POST"])
@limiter.limit(get_rate_limit)
def shorten_url():

    data = request.get_json()

    if not data:
        return jsonify({"error": "request body must be json"}), 400

    long_url = data.get("long_url")

    if not long_url:
        return jsonify({"error": "missing long url"}), 400

    code = generate_unique_code()
    new_url = URL(short_code=code, original_url=long_url)
    db.session.add(new_url)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "failed to save URL, please try again"}), 500

    short_url = f"http://127.0.0.1:5000/{code}"
    return jsonify({"short_url": short_url, "code": code}), 201

@shortener_bp.route("/<code>", methods=["GET"])
@limiter.limit(get_rate_limit)
def redirect_url(code):
    cached_url = redis_client.get(code)
    cached_id  = redis_client.get(f"{code}:id")

    if cached_url is not None and cached_id is not None:
        click = Click(url_id=int(cached_id))
        db.session.add(click)
        db.session.commit()
        return redirect(cached_url, code=302)
    else:
        url = URL.query.filter(URL.short_code == code).first()

        if not url:
            return jsonify({"error": "code not mapped"}), 404

        redis_client.setex(code, 3600, url.original_url)
        redis_client.setex(f"{code}:id", 3600, url.id)

        click = Click(url_id=url.id)
        db.session.add(click)
        db.session.commit()

    return redirect(url.original_url, code=302)

    