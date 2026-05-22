import logging
from groq import (
    Groq,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    GroqError,
)
from app.core.config import GROQ_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)

_FALLBACK = "LLM service is currently unavailable. Please try again later."

_client = Groq(
    api_key=GROQ_API_KEY,
    timeout=30.0,
    max_retries=0,
)


def call_llm(messages: list[dict]) -> str:
    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.3,
        )
        return (response.choices[0].message.content or "").strip()

    except RateLimitError:
        logger.warning("Groq rate limit hit.")
        return _FALLBACK

    except APIConnectionError:
        logger.error("Could not connect to Groq API.")
        return _FALLBACK

    except APITimeoutError:
        logger.error("Groq API request timed out.")
        return _FALLBACK

    except APIStatusError as e:
        logger.error("Groq API returned status %s: %s", e.status_code, e.message)
        return _FALLBACK

    except GroqError as e:
        logger.error("Unexpected Groq error: %s", e)
        return _FALLBACK