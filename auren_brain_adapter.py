# auren_brain_adapter.py
import json
import os

def load_brain_plan(path: str):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_video_from_brain(plan: dict):
    """
    Devuelve el vídeo de mayor prioridad del plan.
    """
    if not plan:
        return None

    videos = plan.get("videos", [])
    if not videos:
        return None

    # elegimos el de prioridad más alta (1 mejor que 2, mejor que 3)
    videos_sorted = sorted(
        videos,
        key=lambda v: v.get("priority", 2)
    )
    chosen = videos_sorted[0]

    return {
        "channel_name": plan.get("channel_name", "Canal_sin_nombre"),
        "niche": plan.get("niche", ""),
        "country": plan.get("country", ""),
        "language": plan.get("language", ""),
        "run_id": plan.get("run_id", ""),
        "video_id": chosen.get("video_id", ""),
        "topic": chosen.get("topic", ""),
        "angle": chosen.get("angle", ""),
        "emotion": chosen.get("emotion", ""),
        "hook": chosen.get("hook", ""),
        "platform": chosen.get("target_platform", "shorts"),
        "affiliate_slot": chosen.get("affiliate_slot", ""),
    }
