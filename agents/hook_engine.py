# agents/hook_engine.py
from typing import Dict, Any
from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN_HOOK_ENGINE.

Misión:
- Generar HOOKS brutales para vídeos cortos (Shorts/Reels/TikTok).
- Tono: directo, elegante, cero humo.
- Cada hook: 1–2 frases máximo.
- No usar mayúsculas completas ni emojis baratos.

Formato de salida SIEMPRE:
HOOKS:
1) ...
2) ...
3) ...
...
"""


def run_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    topic = params.get("topic", "")
    audience = params.get("audience", "")
    emotion = params.get("emotion", "")
    platform = params.get("platform", "")

    user_prompt = f"""
Tema principal: {topic}
Audiencia: {audience}
Emoción objetivo: {emotion}
Plataforma: {platform}

Genera entre 10 y 20 hooks.
"""

    text = run_llm(SYSTEM_PROMPT, user_prompt)
    return {
        "hooks_raw": text,
    }
