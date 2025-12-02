# agents/quality_rater.py
"""
AUREN_QUALITY_RATER
Pone nota 1–10 a un clip según criterios de Auren.

Input:
{
    "clip_text": str,
    "purpose": str  # "awareness" / "afiliado" / "autoridad"...
}

Output:
{
    "score": float,
    "feedback": str
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_QUALITY_RATER.

Eres evaluador interno de Auren Media para clips de vídeo corto.

Criterios (0–10):
- Hook inicial
- Claridad del mensaje
- Ritmo y estructura
- Fuerza emocional
- CTA (si aplica)

Devuelve:
- Nota global 0–10
- Comentario breve de qué mejorar.
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
    clip_text = input_data.get("clip_text", "").strip()
    if not clip_text:
        raise ValueError("Quality Rater: falta 'clip_text'.")

    purpose = input_data.get("purpose", "afiliado")

    user_prompt = f"""
    Clip entre ===:

    ===
    {clip_text}
    ===

    Tipo de clip: {purpose}

    1) Da una nota global de 0 a 10.
    2) Explica brevemente qué está bien y qué mejorar.
    """

    result = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.4,
        max_tokens=800,
    )

    return {"rating_raw": result.strip()}
