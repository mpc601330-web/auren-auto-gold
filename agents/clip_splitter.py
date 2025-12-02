# agents/clip_splitter.py
"""
AUREN_CLIP_SPLITTER
Divide un guion final en 7–12 clips cortos autónomos.

Input:
{
    "script_v2": str,
    "min_clips": int,
    "max_clips": int
}

Output:
{
    "clips_raw": str  # texto con CLIP 1, CLIP 2, ...
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_CLIP_SPLITTER.

Tu trabajo es dividir un guion completo en varios clips cortos
para TikTok, Shorts y Reels.

Reglas:
- Cada clip debe poder funcionar por sí solo.
- Duración objetivo: 20–45 segundos (aprox).
- Cada clip incluye:
  - Título breve
  - Objetivo (educar, inspirar, vender, curiosidad...)
  - Guion en 3–10 líneas

FORMATO EXACTO:

CLIP 1
Título: ...
Objetivo: ...
Guion:
...

---
CLIP 2
Título: ...
Objetivo: ...
Guion:
...

(etc.)
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    script_v2 = input_data.get("script_v2", "").strip()
    if not script_v2:
        raise ValueError("Clip Splitter: falta 'script_v2'.")

    min_clips = input_data.get("min_clips", 7)
    max_clips = input_data.get("max_clips", 12)

    user_prompt = f"""
    Guion completo entre ===:

    ===
    {script_v2}
    ===

    Quiero que lo conviertas en entre {min_clips} y {max_clips} clips cortos,
    siguiendo el formato indicado.
    """

    clips_text = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.75,
        max_tokens=2000,
    )

    return {"clips_raw": clips_text.strip()}
