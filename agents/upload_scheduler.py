# agents/upload_scheduler.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_UPLOAD_SCHEDULER.

A partir de un resumen de audiencia, propones:
- Días ideales de publicación.
- Horas ideales (en hora local).
- Frecuencia semanal.
- Recomendaciones de test A/B.

Formato:

PLAN:
- Días: ...
- Horas: ...
- Frecuencia: ...
- Notas: ...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    audience = params.get("audience", "")
    timezone = params.get("timezone", "Europe/Madrid")

    user_prompt = f"""
Audiencia del canal: {audience}
Zona horaria: {timezone}

Propón un plan de publicación óptimo para Shorts.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "upload_plan_raw": text,
    }
