# auren_brain_adapter.py

import json
from typing import Any, Dict, Optional, List


def load_brain_plan(path: str) -> Dict[str, Any]:
    """
    Carga el JSON de Auren Brain desde disco.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _pick_highest_priority(videos: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Devuelve el vídeo con menor 'priority' (1 = más importante).
    Si hay empate, se queda con el primero.
    """
    if not videos:
        return None

    videos_sorted = sorted(
        videos,
        key=lambda v: v.get("priority", 999)
    )
    return videos_sorted[0]


def pick_video_from_brain(plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Recibe el plan completo de Brain (el JSON que me has pasado)
    y devuelve un dict compacto que AutoGold entiende.

    Estructura de salida:
    {
        "run_id": str,
        "channel_name": str,
        "channel_id": str,
        "country": str,
        "language": str,
        "topic": str,
        "video_id": str,
        "emotion": str,
        "target_platform": str,
        "hook": str,
        "angle": str,
        "est_duration_sec": int,
    }
    """
    videos = plan.get("videos", [])
    video = _pick_highest_priority(videos)
    if not video:
        return None

    return {
        "run_id": plan.get("run_id"),
        "channel_name": plan["channel_name"],
        # si algún día quieres IDs distintos, ya está preparado
        "channel_id": plan.get("channel_id", plan["channel_name"]),
        "country": plan.get("country", "ES"),
        "language": plan.get("language", "es"),

        "topic": video["topic"],
        "video_id": video["video_id"],
        "emotion": video.get("emotion", "Motivador"),
        "target_platform": video.get("target_platform", "shorts"),
        "hook": video.get("hook", ""),
        "angle": video.get("angle", ""),
        "est_duration_sec": int(video.get("est_duration_sec", 60)),
    }
