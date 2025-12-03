# agents/channel_router.py
from slugify import slugify
from agents.topic_scout import TopicSeed
from topic_memory import is_used

# Lista de canales del ecosistema AUREN
CHANNELS = [
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
    }
]


def choose_channel_for_seed(seed: TopicSeed):
    """
    Selecciona el canal adecuado según el niche y país.
    """
    for ch in CHANNELS:
        if ch["niche"] == seed.niche and ch["country"] == seed.country:
            return ch
    return CHANNELS[0]  # fallback seguro


def pick_next_job(seeds: list[TopicSeed]):
    """
    Selecciona SEMILLA + CANAL evitando repeticiones.
    """

    for seed in seeds:
        channel = choose_channel_for_seed(seed)
        topic_slug = slugify(seed.keyword)

        if not is_used(channel["id"], topic_slug):
            return {
                "channel": channel,
                "seed": seed,
                "topic_slug": topic_slug
            }

    return None  # Ya no hay temas nuevos disponibles
