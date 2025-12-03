# agents/channel_router.py
from typing import Dict, Any, List
from agents.topic_scout import TopicSeed
from topic_memory import is_used


def _simple_slug(text: str) -> str:
    """
    Slugificador simple sin dependencias externas.
    """
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9áéíóúñü ]", "", text)
    text = text.replace(" ", "-")
    return re.sub(r"-+", "-", text).strip("-")


# Aquí defines tus canales Auren
CHANNELS: List[Dict[str, Any]] = [
    {
        "id": "auren_dinero_beginners",
        "name": "Auren Dinero para Principiantes",
        "target_level": "beginner",
        "country": "ES",
        "language": "es",
        "niche": "dinero y libertad",
    },
    {
        "id": "auren_dinero_avanzado",
        "name": "Auren Imperio & Cashflow",
        "target_level": "advanced",
        "country": "ES",
        "language": "es",
        "niche": "dinero y libertad",
    },
]


def choose_channel_for_seed(seed: TopicSeed) -> Dict[str, Any]:
    """
    Selecciona el canal adecuado según niche y país.
    """
    for ch in CHANNELS:
        if ch["niche"] == seed.niche and ch["country"] == seed.country:
            return ch
    return CHANNELS[0]  # fallback seguro


def pick_next_job(seeds: List[TopicSeed]):
    """
    Elige (canal + semilla) evitando reutilizar la misma semilla en el mismo canal.
    """
    for seed in seeds:
        channel = choose_channel_for_seed(seed)
        topic_slug = _simple_slug(seed.keyword)

        if not is_used(channel["id"], topic_slug):
            return {
                "channel": channel,
                "seed": seed,
                "topic_slug": topic_slug,
            }

    return None  # no queda nada nuevo
