# auren_brain_adapter.py
"""
Adaptador entre:
- AUREN MEDIA BRAIN (el plan JSON externo: Space / Groq / lo que uses)
- AUREN AUTO GOLD (auto_gold.py)

Responsabilidades:
- Cargar el plan del Brain desde un fichero JSON (ruta en AUREN_BRAIN_PLAN_PATH).
- Normalizar el formato del Brain a un dict sencillo para auto_gold.py.
- Elegir QUÉ vídeo ejecutar hoy (prioridad).

Este módulo NO llama a Groq ni a Gradio.
Solo trabaja con JSON ya generado por el Brain.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from auren_media_brain import slugify  # reutilizamos el slug del Brain local


# ============================================================
# 🧾 CARGA DEL PLAN DEL BRAIN
# ============================================================

def _load_json_from_path(path: str) -> Dict[str, Any]:
    """
    Carga un JSON desde disco.
    Si el contenido es un JSON en string (por ejemplo copiando-pega),
    también lo soporta.
    """
    if not path:
        raise ValueError("Ruta vacía para el Brain plan.")

    # 1) Si existe como fichero, lo abrimos
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 2) Si NO existe como fichero, probamos a interpretarlo como JSON crudo
    trimmed = path.strip()
    if trimmed.startswith("{") or trimmed.startswith("["):
        try:
            return json.loads(trimmed)
        except Exception as e:
            raise ValueError(
                f"El valor de AUREN_BRAIN_PLAN_PATH no es un fichero ni JSON válido: {e}"
            )

    # 3) No es fichero ni JSON
    raise FileNotFoundError(
        f"No se encontró el fichero de Brain plan en '{path}' "
        "y tampoco parece un JSON válido."
    )


def load_brain_plan(path: str) -> Dict[str, Any]:
    """
    Función pública usada por auto_gold.py.

    - Recibe una ruta (AUREN_BRAIN_PLAN_PATH).
    - Devuelve el dict del plan del Brain.
    """
    plan = _load_json_from_path(path)

    # Validación muy ligera
    if not isinstance(plan, dict):
        raise ValueError(f"El plan del Brain debe ser un objeto JSON (dict), no: {type(plan)}")

    if "videos" not in plan:
        # Permitimos, pero avisamos: AutoGold lo notará en pick_video_from_brain
        print("⚠️ El plan del Brain no tiene clave 'videos'. Revisa el JSON de entrada.")

    return plan


# ============================================================
# 🎯 ELECCIÓN DEL VÍDEO A EJECUTAR
# ============================================================

def _normalizar_videos(videos: Any) -> List[Dict[str, Any]]:
    """
    Asegura que 'videos' sea una lista de dicts.
    """
    if videos is None:
        return []
    if isinstance(videos, list):
        return [v for v in videos if isinstance(v, dict)]
    # cualquier otra cosa -> vacío
    return []


def _elegir_video_principal(videos: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Elige un vídeo del plan del Brain.

    Regla sencilla:
    - Ordenar por prioridad (1 es lo más importante).
    - Si hay empate, coger el primero.
    """
    if not videos:
        return None

    def sort_key(v: Dict[str, Any]):
        priority = v.get("priority", 2)
        try:
            priority = int(priority)
        except Exception:
            priority = 2
        # usamos video_id como desempate estable
        vid = v.get("video_id") or v.get("topic") or ""
        return (priority, str(vid))

    sorted_videos = sorted(videos, key=sort_key)
    return sorted_videos[0]


def pick_video_from_brain(plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Recibe el JSON completo del Brain y devuelve un dict NORMALIZADO para auto_gold.py:

    {
        "channel_name": str,
        "topic": str,
        "video_id": str,
        "emotion": str,
        "target_platform": str,
        "country": str,
        "language": str,
        "affiliate_slot": str | None,
    }
    """
    if not isinstance(plan, dict):
        print("⚠️ pick_video_from_brain: plan no es un dict.")
        return None

    videos_raw = plan.get("videos")
    videos = _normalizar_videos(videos_raw)

    if not videos:
        print("⚠️ pick_video_from_brain: el plan no contiene vídeos.")
        return None

    video = _elegir_video_principal(videos)
    if not video:
        print("⚠️ pick_video_from_brain: no se pudo seleccionar vídeo principal.")
        return None

    # Campos de nivel plan
    channel_name = plan.get("channel_name") or "Canal_sin_nombre"
    niche = plan.get("niche") or ""
    country = plan.get("country") or "ES"
    language = plan.get("language") or "es"

    # Campos de nivel vídeo
    topic = video.get("topic") or niche or "Vídeo sin topic definido"
    raw_video_id = video.get("video_id")
    emotion = video.get("emotion") or ""
    target_platform = video.get("target_platform") or "shorts"
    affiliate_slot = video.get("affiliate_slot")

    # Si no hay video_id, generamos uno tipo slug
    if raw_video_id and isinstance(raw_video_id, str):
        video_id = raw_video_id
    else:
        video_id = slugify(topic)

    cfg = {
        "channel_name": channel_name,
        "topic": topic,
        "video_id": video_id,
        "emotion": emotion,
        "target_platform": target_platform,
        "country": country,
        "language": language,
        "affiliate_slot": affiliate_slot,
        # Extra opcional por si lo quieres usar más adelante:
        "niche": niche,
        "run_id": plan.get("run_id"),
        "brain_cycle": plan.get("cycle"),
        "brain_notes": plan.get("notes"),
        "brain_target_date": plan.get("target_date"),
        "brain_reason": video.get("reasons"),
        "brain_hook": video.get("hook"),
        "brain_angle": video.get("angle"),
        "brain_link_to_seed": video.get("link_to_seed"),
    }

    return cfg
