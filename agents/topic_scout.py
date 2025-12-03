# agents/topic_scout.py
from dataclasses import dataclass
from typing import List


@dataclass
class TopicSeed:
    keyword: str   # frase semilla
    niche: str     # nicho general
    country: str
    language: str
    source: str    # "manual", "yt_trends", etc.


def discover_hot_seeds() -> List[TopicSeed]:
    """
    V1: semillas fijas. Luego se sustituye por APIs reales (YouTube, Trends, etc.).
    """
    return [
        TopicSeed("cómo empezar a invertir", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("negocios automáticos con IA", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("máquinas de vending como negocio", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("franquicias rentables en España", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("cómo crear ingresos pasivos reales", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("ahorrar y gestionar dinero con 18 años", "dinero y libertad", "ES", "es", "manual"),
    ]
