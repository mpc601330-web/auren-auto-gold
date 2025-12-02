# agents/emotional_analyzer.py
"""
AUREN_EMOTIONAL_ANALYZER
Analiza la emoción predominante del clip.

Aquí puedes más adelante enchufar un modelo HF específico.
De momento usamos LLM para clasificación rápida.

Input:
{
    "text": str
}

Output:
{
    "emotion_label": str,
    "analysis": str
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_EMOTIONAL_ANALYZER.

Analizas el texto de un clip y determinas:
- emoción principal (miedo, esperanza, motivación, curiosidad, enfado, calma...)
- breves notas sobre por qué.

Devuelve algo muy directo.
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    text = input_data.get("text", "").strip()
    if not text:
        raise ValueError("Emotional Analyzer: falta 'text'.")

    user_prompt = f"""
    Texto entre ===:

    ===
    {text}
    ===

    1) Indica la emoción principal.
    2) Explica en 2–3 frases por qué.
    """

    analysis = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.3,
        max_tokens=600,
    )

    return {"analysis_raw": analysis.strip()}
