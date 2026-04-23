# URL Shortener

A small Flask-based URL shortener with API-key authentication, per-tier rate limiting, Redis caching, PostgreSQL persistence, and click analytics.

## Features

- Generate API keys for users
- Shorten long URLs into compact codes
- Redirect short codes to the original URL
- Track click counts and daily click activity
- Cache API keys and redirect lookups in Redis
- Enforce separate rate limits for `free` and `premium` users

## Project Structure

```text
app/
  __init__.py        # Flask app factory
  auth.py            # API key generation and request authentication
  config.py          # Environment-based configuration
  extensions.py      # Redis client and Flask-Limiter setup
  models.py          # SQLAlchemy models
  routes/
    shortener.py     # Shorten and redirect endpoints
    analytics.py     # Analytics endpoint
migrations/          # Alembic migrations
main.py              # Local entry point
```

## Requirements

- Python 3.14+
- PostgreSQL
- Redis

## Configuration

Create a `.env` file or set environment variables directly.

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | SQLAlchemy connection string for PostgreSQL |
| `REDIS_URL` | No | Redis connection string, defaults to `redis://localhost:6379` |

Example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/url_shortener
REDIS_URL=redis://localhost:6379/0
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Apply database migrations.
4. Start the application.

Example:

```bash
uv sync
```

If you are not using `uv`, install the packages from `pyproject.toml` with your preferred Python tooling.

Run migrations:

```bash
alembic upgrade head
```

Note: Alembic currently reads the database connection from `alembic.ini`. If you change the database URL, update that file or wire environment-based configuration into the Alembic environment first.

Start the app:

```bash
flask --app app:create_app run
```

## Authentication

Most endpoints require the `X-API-KEY` header.

Public endpoints:

- `POST /generate-key`
- `GET /<code>`

## API Endpoints

### `POST /generate-key`

Create a new API key.

Request body:

```json
{
  "username": "alice",
  "tier": "free"
}
```

Valid tiers:

- `free`
- `premium`

Response:

```json
{
  "key": "generated-api-key",
  "tier": "free",
  "user_name": "alice"
}
```

Possible responses:

- `201` created
- `400` missing or invalid input
- `409` username already exists
- `500` unexpected persistence error

### `POST /shorten`

Create a short code for a long URL.

Headers:

- `X-API-KEY: <your-api-key>`

Request body:

```json
{
  "long_url": "https://example.com/some/very/long/path"
}
```

Response:

```json
{
  "short_url": "http://localhost:5000/Ab12Cd",
  "code": "Ab12Cd"
}
```

Possible responses:

- `201` created
- `400` missing or invalid JSON
- `401` missing or invalid API key
- `429` rate limit exceeded
- `500` unexpected persistence error

### `GET /<code>`

Redirect to the original URL for a short code.

Headers:

- `X-API-KEY: <your-api-key>` is required

Possible responses:

- `302` redirect to the original URL
- `404` code not found
- `429` rate limit exceeded

### `GET /stats/<short_code>`

Return analytics for a short code.

Headers:

- `X-API-KEY: <your-api-key>`

Query parameters:

- `page` defaults to `1`
- `per_page` defaults to `7`, maximum `90`

Response includes:

- total click count
- last click timestamp in IST
- click counts grouped by day
- pagination metadata

Example:

```bash
curl -H "X-API-KEY: <your-api-key>" \
  "http://localhost:5000/stats/Ab12Cd?page=1&per_page=7"
```

## Rate Limiting

The app applies tier-based limits through Flask-Limiter.

- `free` users: `10 per minute`
- `premium` users: `100 per minute`
- anonymous or uncached requests fall back to the default limit behavior

## Database Models

- `URL`
  - `short_code`
  - `original_url`
  - `created_at`
- `Click`
  - `url_id`
  - `clicked_at`
- `API`
  - `key`
  - `user_name`
  - `tier`
  - `is_active`
  - `created_at`

## Notes

- Redis is used as a cache for API keys and redirect lookups.
- Generated short URLs use the current request host, so they are not hard-coded to `localhost`.
- Dockerisation is intentionally not included yet and can be added later without changing the API surface.

## Example Workflow

1. Call `POST /generate-key` to create a key.
2. Use that key in the `X-API-KEY` header.
3. Call `POST /shorten` with a long URL.
4. Share the returned short URL.
5. Use `GET /stats/<code>` to inspect clicks.
