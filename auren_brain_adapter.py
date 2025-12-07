# auren_brain_adapter.py
"""
Adaptador entre AUREN AUTO GOLD y el Space remoto AUREN MEDIA BRAIN.

- Llama al endpoint /brain_plan del Space.
- Devuelve un pequeño dict listo para usar en auto_gold.py
  (topic, emoción, plataforma, affiliate_slot, etc.).
"""

import os
import json
from typing import Any, Dict

from gradio_client import Client

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
BRAIN_SPACE_ID = os.getenv("AUREN_BRAIN_SPACE_ID", "").strip()


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


def maybe_enrich_with_brain(
    channel_name: str,
    seed_topic: str,
    topic_slug: str,
    niche: str,
    country: str,
    language: str,
) -> Dict[str, Any] | None:
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

    videos = plan.get("videos") or []
    if not videos:
        print("⚠️ Brain devolvió un plan sin vídeos. Se ignora.")
        return None

    v = videos[0]  # por ahora usamos el primer vídeo del plan

    return {
        "channel_name": plan.get("channel_name") or channel_name,
        "country": plan.get("country") or country,
        "language": plan.get("language") or language,
        "topic": v.get("topic") or seed_topic,
        "video_id": v.get("video_id") or topic_slug,
        "emotion": v.get("emotion") or "aspiracional",
        "target_platform": v.get("target_platform") or "shorts",
        "affiliate_slot": v.get("affiliate_slot"),
    }
