"""
persistence.py
Handles reading and writing of leaderboard.json and settings.json.
All game state that must survive between sessions lives here.
"""
import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# Applied when no settings file exists yet, or a key is missing
DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  "blue",    # blue | red | green | yellow
    "difficulty": "normal",  # easy | normal | hard
}


def load_settings() -> dict:
    """Load settings.json; fall back to defaults for any missing keys."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            # merge: defaults provide values for any key added since last save
            return {**DEFAULT_SETTINGS, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    """Write settings dict to settings.json."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except OSError as e:
        print(f"[persistence] Could not save settings: {e}")


def load_leaderboard() -> list:
    """Return the saved leaderboard list (empty list if file missing/corrupt)."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def save_leaderboard(entries: list) -> list:
    """
    Sort entries by score (descending), keep the top 10, write to file.
    Returns the pruned list.
    """
    entries = sorted(entries, key=lambda e: e["score"], reverse=True)[:10]
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
    except OSError as e:
        print(f"[persistence] Could not save leaderboard: {e}")
    return entries


def add_score(name: str, score: int, distance: int, coins: int) -> list:
    """
    Append a new run result to the leaderboard, trim to top 10, and persist.
    Returns the updated leaderboard list so callers can display it immediately.
    """
    entries = load_leaderboard()
    entries.append({
        "name":     name,
        "score":    score,
        "distance": distance,
        "coins":    coins,
    })
    return save_leaderboard(entries)
