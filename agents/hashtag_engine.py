# agents/hashtag_engine.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_HASHTAG_ENGINE.

Generas conjuntos de hashtags optimizados para:
- TikTok
- YouTube Shorts
- Instagram Reels

Reglas:
- Mezcla hashtags grandes, medios y pequeños.
- Nada de spam genérico (#foryou, etc.).
- Adapta al idioma.

Formato:

[TIKTOK]
#...

[SHORTS]
#...

[REELS]
#...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    topic = params.get("topic", "")
    niche = params.get("niche", "")
    language = params.get("language", "es")

    user_prompt = f"""
Tema del vídeo: {topic}
Nicho: {niche}
Idioma: {language}

Genera conjuntos de hashtags para cada plataforma.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "hashtags_raw": text,
    }
