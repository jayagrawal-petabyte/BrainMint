"""
XSS and basic injection sanitisation utilities.

We use the `bleach` library to strip all HTML tags and attributes from
user-supplied text fields before they are stored in the database or
rendered in emails.  SQLAlchemy parameterised queries protect against
SQL injection at the ORM layer; these helpers handle presentation-layer XSS.
"""
import re
import html


# Characters that indicate potential HTML/script injection
_SCRIPT_PATTERN = re.compile(
    r"<\s*script|javascript\s*:|on\w+\s*=|<\s*iframe|<\s*object|<\s*embed",
    re.IGNORECASE,
)


def strip_html(value: str) -> str:
    """
    Remove all HTML tags and decode HTML entities, leaving plain text.
    Keeps newlines and basic punctuation.
    """
    if not isinstance(value, str):
        return value
    # Remove all tags
    cleaned = re.sub(r"<[^>]+>", "", value)
    # Collapse multiple blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def sanitize_text(value: str) -> str:
    """
    Strip HTML and escape residual HTML entities.
    Use for short text fields (name, service, phone, email display).
    """
    if not isinstance(value, str):
        return value
    return html.escape(strip_html(value))


def sanitize_message(value: str) -> str:
    """
    Strip HTML from the longer free-text message body.
    Preserves newlines for readability.
    """
    if not isinstance(value, str):
        return value
    return strip_html(value)


def has_injection_attempt(value: str) -> bool:
    """
    Heuristic check: returns True if the value looks like it contains
    a script-injection attempt.  Used for logging suspicious requests.
    """
    return bool(_SCRIPT_PATTERN.search(value or ""))


def sanitize_enquiry_fields(
    name: str,
    email: str,
    message: str,
    phone: str | None = None,
    service: str | None = None,
) -> dict:
    """
    Sanitize all enquiry fields and return a dict of clean values.
    """
    return {
        "name": sanitize_text(name),
        "email": sanitize_text(email),
        "phone": sanitize_text(phone) if phone else None,
        "service": sanitize_text(service) if service else None,
        "message": sanitize_message(message),
    }
