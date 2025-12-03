# agents/description_engine.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_DESCRIPTION_ENGINE.

Escribes descripciones optimizadas para YouTube Shorts / Reels:

- 1–2 líneas fuertes arriba.
- 3–5 bullets con valor.
- CTA elegante.
- Incluye 3–5 hashtags relevantes al final.

Formato: texto plano listo para pegar.
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    script = params.get("script_v2", "")
    topic = params.get("topic", "")
    niche = params.get("niche", "")

    user_prompt = f"""
Guion del vídeo:

{script}

Tema: {topic}
Nicho: {niche}

Escribe una descripción lista para YouTube Shorts.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "description_raw": text,
    }
