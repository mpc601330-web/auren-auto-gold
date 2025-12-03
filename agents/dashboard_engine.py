# agents/dashboard_engine.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_DASHBOARD_ENGINE.

Tu trabajo es transformar datos dispersos en un RESUMEN EJECUTIVO
para la Emperatriz:

- 10–15 bullets máximo.
- Muy claro, muy accionable.
- Nada de paja.
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    inputs_raw = params.get("inputs_raw", "")

    user_prompt = f"""
Información de distintos agentes y estadísticas:

{inputs_raw}

Haz un resumen ejecutivo con las 10–15 ideas clave y acciones recomendadas.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "dashboard_summary_raw": text,
    }
