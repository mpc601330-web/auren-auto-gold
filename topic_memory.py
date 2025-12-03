# topic_memory.py
import json
from pathlib import Path

PATH = Path("data/topics_used.json")


def _load():
    if not PATH.exists():
        return {}
    return json.loads(PATH.read_text(encoding="utf-8"))


def _save(data):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def is_used(channel_id: str, topic_slug: str) -> bool:
    data = _load()
    return topic_slug in data.get(channel_id, [])


def mark_used(channel_id: str, topic_slug: str):
    data = _load()
    lst = data.get(channel_id, [])
    if topic_slug not in lst:
        lst.append(topic_slug)
    data[channel_id] = lst
    _save(data)
