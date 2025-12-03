# agents/topic_scout.py
from dataclasses import dataclass

@dataclass
class TopicSeed:
    keyword: str
    niche: str
    country: str
    language: str
    source: str

def discover_hot_seeds() -> list[TopicSeed]:
    """
    V1: Semillas estáticas. Luego se puede conectar a API reales.
    """

    seeds = [
        TopicSeed("cómo empezar a invertir", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("negocios automáticos con IA", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("máquinas de vending como negocio", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("franquicias rentables en España", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("cómo crear ingresos pasivos reales", "dinero y libertad", "ES", "es", "manual"),
        TopicSeed("ahorrar y gestionar dinero con 18 años", "dinero y libertad", "ES", "es", "manual"),
    ]

    return seeds
