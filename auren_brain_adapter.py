# auren_brain_adapter.py
"""
Adaptador entre AUREN AUTO GOLD y AUREN MEDIA BRAIN.

Incluye dos modos:

1) 🔌 Modo remoto (Space HuggingFace)
   - maybe_enrich_with_brain(...) llama al endpoint /brain_plan
     del Space "AUREN-MEDIA-BRAIN" y devuelve una config de vídeo.

2) 📁 Modo archivo local (plan JSON en disco)
   - load_brain_plan(path) lee un JSON con el plan del Brain.
   - pick_video_from_brain(plan) elige un vídeo del plan.
     (usado por auto_gold.py cuando se usa AUREN_BRAIN_PLAN_PATH)

Ambos devuelven una estructura homogénea:
{
    "channel_name": str,
    "country": str,
    "language": str,
    "topic": str,
    "video_id": str,
    "emotion": str,
    "target_platform": str,
    "affiliate_slot": str | None,
}
"""

import os
import json
from typing import Any, Dict, Optional

from gradio_client import Client

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
BRAIN_SPACE_ID = os.getenv("AUREN_BRAIN_SPACE_ID", "").strip()


# =====================================================
# 🔌 CLIENTE REMOTO PARA EL SPACE AUREN MEDIA BRAIN
# =====================================================

def _get_brain_client() -> Client:
    """
    Crea un cliente para el Space del Brain.
    Lanza error si no hay BRAIN_SPACE_ID configurado.
    """
    if not BRAIN_SPACE_ID:
        raise RuntimeError("❌ AUREN_BRAIN_SPACE_ID no está definido en el entorno.")

    if HF_TOKEN:
        # gradio_client usa HF_TOKEN de la variable de entorno
        os.environ["HF_TOKEN"] = HF_TOKEN

    return Client(BRAIN_SPACE_ID)


def _call_brain_plan(
    channel_name: str,
    seed_topic: str,
    topic_slug: str,
    niche: str,
    country: str,
    language: str,
) -> Dict[str, Any]:
    """
    Llama al endpoint /brain_plan del Space AUREN MEDIA BRAIN.
    Devuelve un dict (ya parseado).
    """
    client = _get_brain_client()

    result = client.predict(
        channel_name,
        seed_topic,
        topic_slug,
        niche,
        country,
        language,
        api_name="/brain_plan",   # 👈 coincide con api_name="brain_plan" del Space
    )

    # El Space devuelve dict; si viniera string, intentamos parsear
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except Exception:
            raise RuntimeError(f"Respuesta no JSON del Brain: {result[:200]}")

    if not isinstance(result, dict):
        raise RuntimeError(f"Tipo inesperado desde Brain: {type(result)}")

    return result


def _extract_video_cfg_from_plan(plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normaliza un plan del Brain (sea remoto o desde archivo)
    a la estructura mínima que necesita AutoGold.
    """
    videos = plan.get("videos") or []
    if not videos:
        return None

    v = videos[0]  # por ahora usamos el primer vídeo del plan

    return {
        "channel_name": plan.get("channel_name") or "Canal_sin_nombre",
        "country": plan.get("country") or "ES",
        "language": plan.get("language") or "es",
        "topic": v.get("topic") or v.get("seed_topic") or "tema_sin_titulo",
        "video_id": v.get("video_id") or v.get("topic_slug") or "video_sin_id",
        "emotion": v.get("emotion") or "aspiracional",
        "target_platform": v.get("target_platform") or "shorts",
        "affiliate_slot": v.get("affiliate_slot"),
    }


# =====================================================
# 🟣 API PRINCIPAL PARA AUTO GOLD (modo remoto)
# =====================================================

def maybe_enrich_with_brain(
    channel_name: str,
    seed_topic: str,
    topic_slug: str,
    niche: str,
    country: str,
    language: str,
) -> Optional[Dict[str, Any]]:
    """
    Si hay BRAIN configurado, pide un plan y devuelve la config de un vídeo.
    Si algo falla → devuelve None y Auto Gold sigue con defaults.

    Salida típica:
    {
        "channel_name": "...",
        "country": "ES",
        "language": "es",
        "topic": "...",
        "video_id": "...",
        "emotion": "aspiracional",
        "target_platform": "shorts",
        "affiliate_slot": "curso_inversion",
    }
    """
    if not BRAIN_SPACE_ID:
        # No hay Brain configurado → no hacemos nada.
        return None

    try:
        plan = _call_brain_plan(
            channel_name=channel_name,
            seed_topic=seed_topic,
            topic_slug=topic_slug,
            niche=niche,
            country=country,
            language=language,
        )
    except Exception as e:
        print("⚠️ Error llamando a AUREN MEDIA BRAIN:", e)
        return None

    cfg = _extract_video_cfg_from_plan(plan)
    if not cfg:
        print("⚠️ Brain devolvió un plan sin vídeos. Se ignora.")
        return None

    return cfg


# =====================================================
# 📁 MODO ARCHIVO LOCAL (compatibilidad AUREN_BRAIN_PLAN_PATH)
# =====================================================

def load_brain_plan(path: str) -> Dict[str, Any]:
    """
    Lee un archivo JSON con el plan del Brain.
    Usado cuando se define AUREN_BRAIN_PLAN_PATH en el entorno.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise RuntimeError(f"El archivo de Brain plan no contiene un objeto JSON válido: {path}")

    return data


def pick_video_from_brain(plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Elige un vídeo del plan cargado desde archivo y lo normaliza.
    Misma estructura que maybe_enrich_with_brain.
    """
    return _extract_video_cfg_from_plan(plan)
