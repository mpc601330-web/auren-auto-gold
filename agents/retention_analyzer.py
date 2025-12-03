# agents/retention_analyzer.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_RETENTION_ANALYZER.

Lees un guion y señalas:
- dónde puede caer la atención,
- dónde falta curiosidad,
- dónde conviene un patrón interrupt.

Formato:

ANALISIS:
- ...

SUGERENCIAS:
- Momento X: haz...
- Momento Y: inserta hook visual...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    script = params.get("script_v2", "")

    user_prompt = f"""
Analiza este guion y dime cómo mejorar la retención:

{script}
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "retention_report_raw": text,
    }
