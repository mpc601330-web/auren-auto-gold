# agents/topic_scout_real.py
from typing import Dict, Any, List
from dataclasses import dataclass
from agents.agent_utils import run_llm

@dataclass
class DiscoveredTopic:
    keyword: str
    source: str         # "yt_trends", "google_trends", "twitter", "manual"
    country: str
    language: str
    score: float        # relevancia estimada


SYSTEM_PROMPT = """
Eres AUREN_TOPIC_SCOUT_REAL.

A partir de la descripción del nicho, detectas SUB-TEMAS específicos
que están calientes AHORA MISMO (aunque no tengamos APIs aún, simúlalo
de forma realista).

Devuelve una lista en markdown:

TOPICS:
1) keyword | score=... | source=...
2) ...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    niche = params.get("niche", "")
    country = params.get("country", "ES")
    language = params.get("language", "es")

    user_prompt = f"""
Nicho: {niche}
País objetivo: {country}
Idioma: {language}

Genera entre 10 y 30 sub-temas concretos que estén calientes.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "topics_raw": text,
    }
