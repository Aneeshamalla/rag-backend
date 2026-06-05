import re
import json
from app.llm import call_llm
from app.database import init_bookings_table, save_booking


_EXTRACT_PROMPT = """
Extract interview booking details from the user's message.

STRICT RULES:
- Return ONLY valid JSON
- Do NOT explain anything
- Do NOT add any text outside JSON
- If a field is missing, set it to null

JSON format:
{{
  "name": null,
  "email": null,
  "date": null,
  "time": null
}}

User message: {message}
"""

_BOOKING_KEYWORDS = {"book", "schedule", "interview", "appointment", "slot", "reserve"}
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_booking_intent(text: str) -> bool:
    """Fast keyword check — avoids calling LLM for every message."""
    lowered = text.lower()
    return any(kw in lowered for kw in _BOOKING_KEYWORDS)


def extract_booking_info(user_message: str) -> dict | None:
    """Ask the LLM to extract booking fields. Returns dict or None."""
    prompt = _EXTRACT_PROMPT.format(message=user_message)   # Extract interview booking details...
    raw = call_llm([{"role": "user", "content": prompt}]) # Send to LLM
    try:
        
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip() # Clean LLM output, Removes unwanted formatting like: Removes unwanted formatting like:
        info = json.loads(raw)    # Convert JSON → Python dict
        if all(info.get(k) for k in ("name", "email", "date", "time")):  # Check all fields present, if missing → return None
            if not _EMAIL_RE.match(info["email"]):  # Basic email validation, if invalid → return None
                return None  
            return info
    except (json.JSONDecodeError, AttributeError):
        pass
    return None


def handle_booking(session_id: str, question: str) -> dict | None:
    """Full booking flow: detect → extract → save → return info."""
    if not is_booking_intent(question):
        return None
    info = extract_booking_info(question)
    if info:
        save_booking(   #save booking info to SQLite, with session_id for reference
            session_id=session_id,
            name=info["name"],
            email=info["email"],
            date=info["date"],
            time=info["time"],
        )
        return info
    return None