# agents/ctr_forecaster.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_CTR_FORECASTER.

Recibes un título y una idea de miniatura y estimas:
- CTR esperado (bajo, medio, alto).
- Riesgos.
- Variantes mejores.

Formato:

EVALUACION:
- CTR estimado: ...
- Motivo: ...

VARIANTES:
1) Título + idea miniatura
2) ...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    title = params.get("title", "")
    thumb_brief = params.get("thumbnail_brief", "")

    user_prompt = f"""
Título actual:
{title}

Idea de miniatura:
{thumb_brief}

Evalúa y sugiere mejoras.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "ctr_forecast_raw": text,
    }
