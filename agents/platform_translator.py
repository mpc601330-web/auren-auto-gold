# agents/platform_translator.py
"""
AUREN_PLATFORM_TRANSLATOR
Adapta un mismo clip a TikTok / Shorts / Reels.

Input:
{
    "clip_text": str,
    "base_language": str
}

Output:
{
    "tiktok": str,
    "shorts": str,
    "reels": str
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_PLATFORM_TRANSLATOR.

Tu trabajo es adaptar un mismo clip de texto
a 3 versiones:

- TikTok
- YouTube Shorts
- Instagram Reels

Reglas:
- TikTok: más rápido, directo, informal.
- Shorts: un poco más explicativo, still dinámico.
- Reels: puede ser ligeramente más estético / aspiracional.

Siempre en el mismo idioma que el clip de entrada.

FORMATO EXACTO:

[TIKTOK]
...

[SHORTS]
...

[REELS]
...
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    clip_text = input_data.get("clip_text", "").strip()
    if not clip_text:
        raise ValueError("Platform Translator: falta 'clip_text'.")

    user_prompt = f"""
    Clip base entre ===. Adáptalo a TikTok, Shorts y Reels.

    ===
    {clip_text}
    ===
    """

    translated = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.8,
        max_tokens=1500,
    )

    # Aquí podrías parsear [TIKTOK] / [SHORTS] / [REELS].
    # De momento devolvemos el texto entero y lo parseas luego en auto_gold si quieres.
    return {"platform_versions_raw": translated.strip()}
