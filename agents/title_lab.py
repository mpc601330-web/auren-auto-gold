# agents/title_lab.py
"""
AUREN_TITLE_LAB
Genera 5–10 títulos con alto CTR por clip y plataforma.

Input:
{
    "clip_text": str,
    "platform": str
}

Output:
{
    "titles_raw": str
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_TITLE_LAB.

Eres especialista en títulos para vídeos cortos de alto CTR
en TikTok, YouTube Shorts y Reels.

Reglas:
- Crea títulos que la gente QUIERA abrir.
- Usa curiosidad, beneficio claro, urgencia elegante.
- No uses mayúsculas completas, ni spam cutre.
- No prometas cifras falsas.

FORMATO:

1) ...
2) ...
3) ...
...
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    clip_text = input_data.get("clip_text", "").strip()
    if not clip_text:
        raise ValueError("Title Lab: falta 'clip_text'.")

    platform = input_data.get("platform", "TikTok")

    user_prompt = f"""
    Texto del clip entre ===:

    ===
    {clip_text}
    ===

    Genera 5–10 títulos posibles optimizados para {platform},
    siguiendo las reglas y el formato indicado.
    """

    titles_text = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.85,
        max_tokens=800,
    )

    return {"titles_raw": titles_text.strip()}
