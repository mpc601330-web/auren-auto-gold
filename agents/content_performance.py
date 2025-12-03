# agents/content_performance.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_CONTENT_PERFORMANCE_ENGINE.

Analizas estadísticas de vídeos (views, CTR, retención, etc.)
y detectas patrones:

- qué tipo de hooks funcionan mejor,
- duración ideal,
- temas que más convierten.

Formato:

RESUMEN:
- ...

INSIGHTS:
1) Insight X...
2) ...

ACCIONES RECOMENDADAS:
- ...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    stats_raw = params.get("stats_raw", "")

    user_prompt = f"""
Datos históricos del canal:

{stats_raw}

Analiza y extrae patrones y acciones claras.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "performance_report_raw": text,
    }
