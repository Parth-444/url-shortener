import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import g

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_api_key_identity():
    user = g.get("current_user")
    return user["key"] if user else get_remote_address()

limiter = Limiter(key_func=get_api_key_identity)

def get_rate_limit():
    tier = g.get("current_user", {}).get("tier")
    if tier == "free":
        return "10 per minute"
    if tier == "premium":
        return "100 per minute"
    return "10 per minute"