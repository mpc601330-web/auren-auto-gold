# agents/novelty_detector.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_NOVELTY_DETECTOR.

Analizas una lista de temas y decides cuáles son:
- "saturados",
- "estables",
- "emergentes",
- "ultra_nuevos".

Tu foco es encontrar oportunidades nuevas antes de que revienten.

Formato SIEMPRE:

ANALISIS:
- Resumen general...

CLASIFICACION:
- Tema X: etiqueta, motivo
- Tema Y: ...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    topics_raw = params.get("topics_raw", "")

    user_prompt = f"""
Lista de temas:

{topics_raw}

Clasifícalos según saturación y novedad, y resalta los 5 más prometedores.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "novelty_report_raw": text,
    }
