from flask import g, request, jsonify, Blueprint
from app.extensions import redis_client
from app.models import API, db
import secrets

EXEMPT_ENDPOINTS = {"shortener.redirect_url", "auth_bp.generate_key"}

auth_bp = Blueprint("auth_bp", __name__)



@auth_bp.route("/generate-key", methods=["POST"])
def generate_key():
    """
    Generate a new API key for a user.

    Expects a JSON body:
        {
            "username": str,   # unique username, required
            "tier":     str    # access tier, required — must be "free" or "premium"
        }

    Returns:
        201  { "key": str, "tier": str, "user_name": str }
        400  if body is missing, or username/tier is absent
        400  if tier is not "free" or "premium"
        409  if username is already registered
        500  if the key could not be saved
    """
    data = request.get_json()
     
    if not data:
        return jsonify({"error": "No credentials"}), 400

    username = data.get("username")
    tier = data.get("tier")

    if not username or not tier:
        return jsonify({"error": "Missing username or tier"}), 400

    if tier not in ["free", "premium"]:
        return jsonify({"error": "Invalid tier"}), 400

    if API.query.filter(API.user_name == username).first():
        return jsonify({"error": "User name already exists"}), 409
    
    generated_key = secrets.token_hex(32)

    try:
        db.session.add(API(user_name=username, key=generated_key, tier=tier, is_active=True))
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "failed to generate key, please try again"}), 500
    
    redis_client.setex(f"apikey:{generated_key}:tier", 3600, tier)
    redis_client.setex(f"apikey:{generated_key}:user_name", 3600, username)
    

    return jsonify({"key": generated_key, "tier": tier, "user_name": username}), 201


def verify_api_key():
    if request.endpoint in EXEMPT_ENDPOINTS:
        return

    api_key = request.headers.get("X-API-KEY")

    if not api_key:
        return jsonify({"error": "API key required"}), 401

    cached_tier = redis_client.get(f"apikey:{api_key}:tier")
    cached_user = redis_client.get(f"apikey:{api_key}:user_name")

    if cached_tier and cached_user:
        g.current_user = {
            "key": api_key,
            "tier": cached_tier,
            "user_name": cached_user
        }
        return

    key_from_database = API.query.filter_by(key=api_key, is_active=True).first()
    if not key_from_database:
        return jsonify({"error": "Invalid API key"}), 401

    redis_client.setex(f"apikey:{api_key}:tier", 3600, key_from_database.tier)
    redis_client.setex(f"apikey:{api_key}:user_name", 3600, key_from_database.user_name)

    g.current_user = {
        "key": api_key,
        "tier": key_from_database.tier,
        "user_name": key_from_database.user_name
    }
