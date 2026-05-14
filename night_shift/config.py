"""Night Shift – constants and JSON config persistence."""

import json
import os

TEMP_MIN = 1000
TEMP_MAX = 6500
CONFIG_FILE = os.path.expanduser('~/.config/night-shift.json')

PRESETS = [
    ("Day",    6500),
    ("Office", 5000),
    ("Sunset", 3400),
    ("Night",  2300),
    ("Deep",   1200),
]


def load() -> dict:
    defaults = {'temp': 4500, 'on': False}
    try:
        if os.path.exists(CONFIG_FILE):
            defaults.update(json.load(open(CONFIG_FILE)))
    except Exception:
        pass
    defaults['temp'] = max(TEMP_MIN, min(TEMP_MAX, defaults['temp']))
    return defaults


def save(cfg: dict) -> None:
    os.makedirs(os.path.dirname(CONFIG_FILE) or '.', exist_ok=True)
    json.dump(cfg, open(CONFIG_FILE, 'w'), indent=2)
