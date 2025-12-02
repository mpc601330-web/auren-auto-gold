# agents/angle_master.py
"""
AUREN_ANGLE_MASTER
Genera 10–15 ángulos + hooks virales a partir de un tema y un público.

Input (dict):
{
    "topic": str,
    "audience": str,
    "emotion": str,
    "platform": str,
    "num_angles": int
}

Output (dict):
{
    "angles_raw": str  # texto ya formateado
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_ANGLE_MASTER.

Eres estratega creativo para vídeos cortos (TikTok, YouTube Shorts, Reels)
sobre dinero, IA, negocios y productividad.

Tu trabajo:
- Convertir un tema general en 10–15 ÁNGULOS potentes.
- Cada ángulo incluye:
  - Nombre breve
  - 1 hook de una sola frase

Reglas:
- Mezcla: miedo elegante, oportunidad, aspiracional, educativo, curiosidad.
- Nada de spam barato ni promesas falsas.
- Tono: profesional, estratégico, con energía Pendragon.

FORMATO EXACTO:

1) [Nombre del ángulo]
Hook: ...

2) [Nombre del ángulo]
Hook: ...

...

Nada de explicaciones extra fuera de esa lista.
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    topic = input_data.get("topic", "").strip()
    audience = input_data.get("audience", "").strip()
    emotion = input_data.get("emotion", "motivador").strip()
    platform = input_data.get("platform", "TikTok / Shorts / Reels").strip()
    num_angles = input_data.get("num_angles", 12)

    if not topic:
        raise ValueError("Angle Master: falta 'topic' en input_data.")

    user_prompt = f"""
    Tema central: {topic}

    Público objetivo: {audience}
    Emoción objetivo: {emotion}
    Plataforma principal: {platform}
    Número aproximado de ángulos: {num_angles}

    Genera ángulos para contenido de alto rendimiento y potencial de afiliados
    (Hotmart + SaaS), con hooks que despierten curiosidad y acción.
    """

    angles_text = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.85,
        max_tokens=1400,
    )

    return {"angles_raw": angles_text}
