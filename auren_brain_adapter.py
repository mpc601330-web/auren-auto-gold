"""
auren_brain_adapter.py

Adapter entre el archivo de plan del BRAIN y auto_gold.py.

Expone dos funciones:

- load_brain_plan(path: str) -> dict
- pick_video_from_brain(plan: dict) -> dict | None

Formato esperado del JSON del Brain (v1):

{
  "meta": {...},
  "videos": [
    {
      "video_id": "auren-2025-12-05-001",
      "channel_name": "Auren Dinero para Principiantes",
      "topic": "cómo empezar a invertir para principiantes",
      "emotion": "motivador",
      "target_platform": "shorts",
      "country": "ES",
      "language": "es",
      "affiliate_slot": "curso_inversion_principiantes"
    }
  ]
}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def load_brain_plan(path: str) -> Dict[str, Any]:
    """
    Carga el JSON de plan del Brain desde el path indicado.

    - Si el fichero no existe o está mal formado, lanza una excepción clara.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"[AUREN_BRAIN] No se encontró el plan en: {p}")

    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"[AUREN_BRAIN] JSON inválido en {p}: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"[AUREN_BRAIN] El plan debe ser un objeto JSON de nivel raíz, no {type(data)}")

    return data


def _normalize_video_cfg(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza un bloque de vídeo del Brain para que auto_gold.py
    pueda usarlo sin reventar.

    Asegura que existan estas claves:
    - video_id
    - channel_name
    - topic
    - emotion
    - target_platform
    - country
    - language
    - affiliate_slot (opcional)
    """
    # Campos obligatorios mínimos
    required = ["video_id", "channel_name", "topic", "country", "language"]
    for key in required:
        if key not in raw or not str(raw[key]).strip():
            raise ValueError(f"[AUREN_BRAIN] Falta campo obligatorio '{key}' en el vídeo del plan: {raw}")

    # Defaults razonables
    emotion = (str(raw.get("emotion") or "motivador")).strip()
    target_platform = (str(raw.get("target_platform") or "shorts")).strip()

    cfg: Dict[str, Any] = {
        "video_id": str(raw["video_id"]),
        "channel_name": str(raw["channel_name"]),
        "topic": str(raw["topic"]),
        "country": str(raw["country"]),
        "language": str(raw["language"]),
        "emotion": emotion,
        "target_platform": target_platform,
        # opcionales
        "affiliate_slot": raw.get("affiliate_slot"),
        "priority": raw.get("priority", "normal"),
        "notes": raw.get("notes", ""),
    }

    return cfg


def pick_video_from_brain(plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Selecciona UN vídeo del plan del Brain.

    Versión v1 (simple): coge el primer vídeo de la lista "videos".
    Más adelante se puede mejorar para:
    - filtrar por estado (pending / done)
    - usar prioridades
    - usar fecha
    """
    videos = plan.get("videos") or []
    if not isinstance(videos, list) or not videos:
        # Nada que producir hoy
        return None

    # v1: simplemente el primero
    raw_video = videos[0]
    if not isinstance(raw_video, dict):
        raise ValueError(f"[AUREN_BRAIN] Vídeo inválido en el plan: {raw_video}")

    return _normalize_video_cfg(raw_video)
