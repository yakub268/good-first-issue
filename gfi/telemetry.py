"""Privacy-focused telemetry for live activity feed."""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional


TELEMETRY_FILE = Path.home() / ".gfi-telemetry.json"
TELEMETRY_ENABLED_FILE = Path.home() / ".gfi-telemetry-enabled"


def is_enabled() -> bool:
    """Check if telemetry is enabled."""
    return TELEMETRY_ENABLED_FILE.exists()


def enable_telemetry():
    """Enable telemetry."""
    TELEMETRY_ENABLED_FILE.touch()


def disable_telemetry():
    """Disable telemetry."""
    if TELEMETRY_ENABLED_FILE.exists():
        TELEMETRY_ENABLED_FILE.unlink()


def get_anonymous_id(username: str) -> str:
    """Generate anonymous ID from username (one-way hash)."""
    return hashlib.sha256(username.encode()).hexdigest()[:12]


def log_event(event_type: str, data: dict = None, username: str = None):
    """Log a telemetry event (if enabled)."""

    if not is_enabled():
        return

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "user_id": get_anonymous_id(username) if username else None,
        "data": data or {},
    }

    # Append to local file (for potential upload later)
    events = []
    if TELEMETRY_FILE.exists():
        try:
            events = json.loads(TELEMETRY_FILE.read_text())
        except:
            events = []

    events.append(event)

    # Keep only last 100 events locally
    events = events[-100:]

    TELEMETRY_FILE.write_text(json.dumps(events, indent=2))


def get_stats() -> dict:
    """Get aggregated stats from telemetry (mock for now)."""

    # In production, this would query a backend API
    # For now, return placeholder data
    return {
        "searches_today": 127,
        "issues_found": 1547,
        "recent_activity": [
            {"type": "search", "language": "Python", "time": "2 min ago"},
            {"type": "find", "score": 0.89, "time": "5 min ago"},
            {"type": "success", "repo": "django/django", "time": "12 min ago"},
        ],
        "trending_languages": ["Python", "JavaScript", "Rust", "Go"],
    }


def display_stats(console):
    """Display live activity stats in CLI."""

    if not is_enabled():
        return

    stats = get_stats()

    console.print(f"\n[dim]Live stats: {stats['searches_today']} searches today, "
                  f"{stats['issues_found']} issues found this week[/dim]")
