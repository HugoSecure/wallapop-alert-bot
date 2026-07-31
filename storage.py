import json
import os
import time

STORAGE_FILE = "seen_ads.json"
PURGE_AFTER_SECONDS = 30 * 24 * 3600


def _load():
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_new(ad_id):
    return ad_id not in _load()


def mark_seen(ad_id):
    now = time.time()
    data = _load()
    data[ad_id] = int(now)
    data = {k: v for k, v in data.items() if now - v <= PURGE_AFTER_SECONDS}
    _save(data)
