import json
import redis
import redis.exceptions
from app.core.config import REDIS_URL

_client = redis.from_url(REDIS_URL, decode_responses=True)

HISTORY_LIMIT = 10


def get_history(session_id: str) -> list[dict]:
    try:
        raw = _client.get(f"chat:{session_id}")
        return json.loads(raw) if raw else []
    except redis.exceptions.RedisError:
        # Redis down → return empty memory safely
        return []


def add_to_history(session_id: str, role: str, content: str) -> None:
    try:
        history = get_history(session_id)
        history.append({"role": role, "content": content})

        history = history[-(HISTORY_LIMIT * 2):]

        _client.set(
            f"chat:{session_id}",
            json.dumps(history),
            ex=3600
        )

    except redis.exceptions.RedisError:
        # Redis down → skip memory saving, do NOT crash API
        pass


def clear_history(session_id: str) -> None:
    try:
        _client.delete(f"chat:{session_id}")
    except redis.exceptions.RedisError:
        pass