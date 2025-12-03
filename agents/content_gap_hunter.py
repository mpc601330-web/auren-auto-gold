# agents/content_gap_hunter.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_CONTENT_GAP_HUNTER.

Miras lo que ya existe en un nicho (videos típicos, enfoques,
formatos) y detectas:
- temas NO tratados,
- ángulos diferentes,
- formatos infrautilizados.

Formato:

RESUMEN:
- ...

GAPS:
1) Gap X: descripción, por qué es oportunidad, idea de vídeo ejemplo.
2) ...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    niche = params.get("niche", "")
    competitor_notes = params.get("competitor_notes", "")

    user_prompt = f"""
Nicho: {niche}

Resumen de lo que hace la competencia:
{competitor_notes}

Detecta al menos 10 gaps claros.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "gaps_raw": text,
    }
