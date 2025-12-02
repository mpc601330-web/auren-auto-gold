# agents/thumbnail_brief.py
"""
AUREN_THUMBNAIL_BRIEF
Genera el concepto visual + texto para miniatura.

Input:
{
    "clip_text": str,
    "best_title": str
}

Output:
{
    "brief": str
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_THUMBNAIL_BRIEF.

Diseñas el concepto de miniaturas para vídeos cortos
sobre dinero, IA y productividad.

Tu trabajo:
- Proponer qué debe verse en la miniatura.
- Proponer 1–3 palabras de texto dentro de la miniatura.
- Opcionalmente, un prompt para IA de imagen.

FORMATO:

CONCEPTO VISUAL:
...

TEXTO EN MINIATURA:
...

PROMPT IA (opcional):
...
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    clip_text = input_data.get("clip_text", "").strip()
    best_title = input_data.get("best_title", "").strip()

    if not clip_text:
        raise ValueError("Thumbnail Brief: falta 'clip_text'.")

    user_prompt = f"""
    Clip entre ===:

    ===
    {clip_text}
    ===

    Título principal:
    {best_title}

    Genera el brief completo siguiendo el formato.
    """

    brief = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.9,
        max_tokens=1000,
    )

    return {"brief": brief.strip()}
