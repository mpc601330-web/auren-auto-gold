# agents/opportunity_scorer.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_OPPORTUNITY_SCORER.

Tu misión: puntuar temas por potencial económico:
- dificultad (0–10)
- competencia (0–10)
- monetización posible (0–10)
- longevidad del tema (0–10)

Devuelve una tabla markdown:

| # | Tema | Dificultad | Competencia | Monetización | Longevidad | Score Total |
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    topics_raw = params.get("topics_raw", "")

    user_prompt = f"""
Analiza estos temas y crea la tabla con puntuaciones y score total:

{topics_raw}
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "opportunity_table_raw": text,
    }
